import asyncio
import logging


class NBUSocket:
    """
    Abstract base class for all NetBackup sockets
    """

    def __init__(self, host, port, timeout=5, quiet=False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.quiet = quiet
        self._reader = self._writer = None

    @property
    def reader(self):
        if not self._reader:
            raise RuntimeError("Socket is not connected")
        return self._reader

    @property
    def writer(self):
        if not self._writer:
            raise RuntimeError("Socket is not connected")
        return self._writer

    async def sendall(self, data):
        if not self.quiet:
            logging.debug("Sending %s to %s:%d", data, self.host, self.port)

        async with asyncio.timeout(self.timeout):
            self.writer.write(data)
            await self.writer.drain()

    async def send_pkt(self, payload):
        await self.sendall(len(payload).to_bytes(4, "big") + payload)

    async def recv(self, length=4096):
        async with asyncio.timeout(self.timeout):
            data = await self.reader.read(length)

        if not self.quiet:
            logging.debug("Read %s from %s:%d", data, self.host, self.port)
        return data

    async def recv_pkt(self):
        size = await self.recv(4)
        size = int.from_bytes(size, "big")
        return await self.recv(size)

    async def connect(self):
        try:
            async with asyncio.timeout(self.timeout):
                self._reader, self._writer = await asyncio.open_connection(
                    self.host, self.port
                )
        except TimeoutError:
            e = TimeoutError(f"[Errno 60] Operation timed out")
            logging.info("Failed to connect to %s:%d: %s", self.host, self.port, e)
            raise e
        except Exception as e:
            logging.info("Failed to connect to %s:%d: %s", self.host, self.port, e)
            raise e

    async def handshake(self):
        pass

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
        self._reader = self._writer = None


class PBXSocket(NBUSocket):
    """
    Helper class to communicate with the pbx_exchange process
    """

    def __init__(self, host, port=1556, **kwargs):
        super().__init__(host, port, **kwargs)

    async def handshake(self, extension):
        msg = "ack=1\nextension={ext}\n\n".format(ext=extension)
        logging.debug(
            "[PBXSocket] Performing handshake with %s:%d for extension %s",
            self.host,
            self.port,
            extension,
        )
        await self.sendall(msg.encode())
        if not await self.recv():
            raise RuntimeError(
                f"{extension} not available through pbx_exchange for {self.host}:{self.port}"
            )


class VNETDSocket(NBUSocket):
    """
    Helper class to communicate with the vnetd process
    """

    def __init__(self, host, use_pbx=True, **kwargs):
        port = 1556 if use_pbx else 13724
        super().__init__(host, port, **kwargs)
        self.use_pbx = use_pbx

    @property
    def writer(self):
        return self.sock.writer

    @property
    def reader(self):
        return self.sock.reader

    async def connect(self):
        # No need to catch errors for logging purposes as it is already handled
        # by the underlying sockets
        if self.use_pbx:
            logging.debug(
                "[VNETDSocket] Attempting to connect to vnetd through pbx_exchange on %s:%d",
                self.host,
                self.port,
            )
            self.sock = PBXSocket(self.host, timeout=self.timeout, quiet=True)
            await self.sock.connect()
            await self.sock.handshake("vnetd")
        else:
            logging.debug(
                "[VNETDSocket] Attempting to connect directly to vnetd on %s:%d",
                self.host,
                self.port,
            )
            self.sock = NBUSocket(
                self.host, self.port, timeout=self.timeout, quiet=True
            )
            await self.sock.connect()
            await self.sock.handshake()

    async def handshake(self):
        # Perform vnetd version handshake
        await self.sendall(b"4\x00")
        ver = await self.recv()
        await self.sendall(ver)

    async def read_value(self) -> bytes:
        data = await self.sock.recv(1)
        while data and data[-1] != 0:
            data += await self.sock.recv(1)
        logging.debug("Read %s from %s:%d", data, self.host, self.port)
        return data

    async def read_string(self) -> str:
        val = await self.read_value()
        return val.rstrip(b"\x00").decode()

    async def read_int(self) -> int:
        try:
            return int(await self.read_string())
        except ValueError:
            return None

    async def get_version(self) -> str:
        logging.debug(
            "[VNETDSocket] Sending VN_VERSION_GET to vnetd on %s:%d",
            self.host,
            self.port,
        )
        await self.sendall(b"8\x00")
        version = await self.read_string()
        ret_code = await self.read_value()
        return version

    async def get_security_info(self) -> dict:
        logging.debug(
            "[VNETDSocket] Sending VN_REQUEST_GET_SECURITY_INFO to vnetd on %s:%d",
            self.host,
            self.port,
        )
        await self.sendall(b"9\x00")
        ret_code = await self.read_value()

        out = {}
        if ret_code != b"0\x00":
            logging.debug(
                "[VNETDSocket] Got unexpected response from vnetd %s:%d: %s",
                self.host,
                self.port,
                ret_code,
            )
            return out

        # Send this first so we get the "raw" ports from bp.conf instead of the
        # "resolved" one (most of the time the raw ones are "0" for "default")
        # We do this so the result is as close to the original bp.conf as
        # possible
        await self.sendall(b"ni_ess_available\x00")

        # See https://www.veritas.com/content/support/en_US/doc/18716246-126559472-0/v40574999-126559472
        await self.sendall(b"ni_use_vxss\x00")
        out["USE_VXSS"] = await self.read_int()

        # See https://www.veritas.com/content/support/en_US/doc/18716246-126559472-0/v101111836-126559472
        await self.sendall(b"ni_use_at\x00")
        out["USE_AUTHENTICATION"] = await self.read_int()

        # See https://www.veritas.com/content/support/en_US/doc/18716246-126559472-0/v40554370-126559472
        await self.sendall(b"ni_authorization_service\x00")
        out["AUTHORIZATION_SERVICE"] = {
            "host": await self.read_string(),
            "port": await self.read_int(),
        }

        # See https://www.veritas.com/content/support/en_US/doc/18716246-126559472-0/v40491531-126559472
        await self.sendall(b"ni_authentication_domains\x00")
        _ = await self.recv(1)
        domains = []
        while True:
            broker = await self.read_value()
            if broker == b"\x00":
                break
            domains.append(
                {
                    "broker": broker.rstrip(b"\x00").decode(),
                    "port": await self.read_int(),
                    "domain": await self.read_string(),
                    "comment": await self.read_string(),
                    "mechanism": await self.read_int(),
                }
            )
        out["AUTHENTICATION_DOMAIN"] = domains

        # See https://www.veritas.com/content/support/en_US/doc/18716246-126559472-0/v40575005-126559472
        await self.sendall(b"ni_vxss_networks\x00")
        networks = []
        while True:
            host = await self.read_value()
            if host == b"\x00":
                break
            networks.append(
                {
                    "network": host.rstrip(b"\x00").decode(),
                    "use_vxss": await self.read_int(),
                }
            )
        out["VXSS_NETWORK"] = networks

        return out

    async def get_primary_server(self) -> str:
        logging.debug(
            "[VNETDSocket] Sending VN_REQUEST_MASTER_NAME to vnetd on %s:%d",
            self.host,
            self.port,
        )
        await self.sendall(b"14\x00")
        server = await self.read_string()
        ret_code = await self.read_value()
        return server
