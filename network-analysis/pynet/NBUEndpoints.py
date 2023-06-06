import socket
import ssl
import struct

from threading import Condition,Lock

from pynet.endpoint import *
from pynet.endpoints.socket import *

def get_extension(data):
    x = data.split(b"extension=")
    return x[1].strip()


class NBUService(object):
    def __init__(self,sock,certificate,key):
        self.sock = sock
        self.certificate = certificate
        self.key = key
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        self.ssl_context.load_cert_chain(self.certificate,self.key)
        self.lock = Lock()
        self.cond = Condition()
        self.wait_for_tls = False

        # Start TLS
        self.tls = False
        self.next_pkt_to_receive = 0
        self.next_pkt_to_send = 0

        # json
        self.json_received = False
        self.json_sent = False

    def raw_send(self,data):
        self.sock.send(data)
        self.next_pkt_to_send += 1

    def raw_recv(self):
        #print("%r receving %r" % (self,self.next_pkt_to_receive))
        data = self.sock.recv(4096)
        self.next_pkt_to_receive += 1
        return data

    def send(self,data):
        #print("%r pkt : len:%r num:%r" % (self,len(data),self.next_pkt_to_send))
        if self.next_pkt_to_send == self.JSON_PKT_SENT:
            self.json_sent = True
            self.raw_send(data)
            #print("%r json sent %r" % (self,len(data)))
            if self.json_received:
                with self.lock:
                    if not self.tls:
                        self.start_tls(False)
        else:
            self.raw_send(data)

    def recv(self):
        if self.next_pkt_to_receive == self.JSON_PKT_RECEIVED:
            data = self.receive_json()
            self.json_received = True
            self.wait_for_tls = True
            #print("%r json received" % (self,))
        else:
            self.lock.acquire()
            if not self.tls and self.wait_for_tls:
                with self.cond:
                    self.lock.release()
                    #print("%r block on cond" % self)
                    self.cond.wait()
                    #print("%r unblock on cond" % self)
                    self.wait_for_tls = False
            else:
                self.lock.release()
            data = self.raw_recv()
        if self.json_received and self.json_sent:
            with self.lock:
                if not self.tls:
                    self.start_tls(True)
        return data

    def receive_json(self):
        pkt = self.raw_recv()
        sz = struct.unpack(">H",pkt[6:8])[0] + 8
        while sz != len(pkt):
            pkt += self.raw_recv()
        return pkt

    def start_tls(self,b):
        self.tls = True
        print("%r STARTING TLS %r" % (self,b))
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.sock = self.ssl_context.wrap_socket(self.sock,server_side=self.TLS_SERVER_SIDE)
        with self.cond:
            self.cond.notify()
        print("%r STARTED TLS" % (self,))

    def close(self):
        self.sock.close()


class ServiceNBUListen(NBUService):
    TLS_SERVER_SIDE = True


class ServiceNBU(NBUService):
    TLS_SERVER_SIDE = False


class BPCD(ServiceNBU):
    JSON_PKT_SENT = 0
    JSON_PKT_RECEIVED = 0

class BPCDListen(ServiceNBUListen):
    JSON_PKT_SENT = 0
    JSON_PKT_RECEIVED = 0

class VNETD(ServiceNBU):
    JSON_PKT_SENT = 2
    JSON_PKT_RECEIVED = 1

class VNETDListen(ServiceNBUListen):
    JSON_PKT_SENT = 1
    JSON_PKT_RECEIVED = 2


@Endpoint.register
class PBX(TCP):
    SWITCH = {b"bpcd":BPCD,b"vnetd":VNETD}
    
    @classmethod
    def set_cli_arguments(cls,parser):
        TCP.set_cli_arguments(parser)
        tls = parser.add_argument_group('TLS',"TLS specific options")
        tls.add_argument("-c","--certificate",metavar="PATH",help="Certificate file for client authentication")
        tls.add_argument("-k","--key",metavar="PATH",help="Key file for client authentication")

    def __init__(self,certificate,key,*args,**kargs):
        super().__init__(*args,**kargs)
        self.certificate = certificate
        self.key = key
        self.ext = None
        self.next_pkt_sent = 0
        self.next_pkt_received = 0

    def handle_send(self,data):
        if self.next_pkt_sent == 0:
            ext = get_extension(data)
            if ext in PBX.SWITCH:
                self.ext = PBX.SWITCH[ext](self.sock,self.certificate,self.key)
        self.next_pkt_sent += 1

    def send(self,data):
        try:
            if self.ext:
                self.ext.send(data)
            else:
                super().send(data)
            self.handle_send(data)
        except (ssl.SSLEOFError,ssl.SSLZeroReturnError):
            raise EndpointClose()

    def recv(self):
        try:
            if self.next_pkt_received > 0 and self.ext:
                self.next_pkt_received += 1
                return self.ext.recv()
            else:
                self.next_pkt_received += 1
                return super().recv()
        except (ssl.SSLEOFError,ssl.SSLZeroReturnError):
            raise EndpointClose()

    def close(self):
        print("closing")
        if self.ext:
            self.ext.close()
        else:
            super().close()


@Endpoint.register
class PBXListen(TCP_LISTEN):
    SWITCH = {b"bpcd":BPCDListen,b"vnetd":VNETDListen}

    @classmethod
    def set_cli_arguments(cls,parser):
        TCP_LISTEN.set_cli_arguments(parser)
        tls = parser.add_argument_group('TLS',"TLS specific options")
        tls.add_argument("-c","--certificate",metavar="PATH",help="Certificate server")
        tls.add_argument("-k","--key",metavar="PATH",help="Key")

    def __init__(self,certificate,key,*args,**kargs):
        super().__init__(*args,**kargs)
        self.certificate = certificate
        self.key = key
        self.ext = None
        self.next_pkt_recv = 0
        self.next_pkt_sent = 0

    def get_conf(self):
        return {"certificate":self.certificate, "key":self.key}

    def handle_recv(self,data):
        if self.next_pkt_recv == 0:
            ext = get_extension(data)
            if ext in PBXListen.SWITCH:
                print("RECEIVED switching to %r" % (ext,))
                self.ext = PBXListen.SWITCH[ext](self.sock,self.certificate,self.key)
        self.next_pkt_recv += 1

    def recv(self):
        try:
            if self.ext:
                data = self.ext.recv()
            else:
                data = super().recv()
            self.handle_recv(data)
        except (ssl.SSLEOFError,ssl.SSLZeroReturnError):
            raise EndpointClose()
        return data

    def send(self,data):
        try:
            if self.next_pkt_sent > 0 and self.ext:
                self.ext.send(data)
            else:
                data = super().send(data)
            self.next_pkt_sent += 1
        except (ssl.SSLEOFError,ssl.SSLZeroReturnError):
            raise EndpointClose()

    def close(self):
        if self.ext:
            self.ext.close()
        else:
            super().close()


