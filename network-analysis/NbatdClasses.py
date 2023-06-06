from scapy import *
from scapy.packet import *
from scapy.fields import *

NBATD_MSG_TYPES = {
    0x01: "PK_AUTH_OK",
    0x02: "PING_2",
    0x04: "PING_4",
    0x08: "PING_8",
    0x0D: "PING_D",
    0x03: "PK_AUTH_QUERY",
    0x05: "PK_AUTH_DATA",
    0x06: "PK_AUTH_TYPE",
    0x07: "PK_AUTH_PUBLIC_KEY",
    0x0C: "CERTIFICATE_REQUEST",
    0x0E: "PK_AUTH_DATA_PLUGIN_SPECIFIC",
    0x0F: "PK_RENEWAL_DATA",
    0x10: "PK_WEBCREDENTIAL_DATA",
    0x32: "PK_AUTH_CSR",
    0x11: "PK_VALIDATE_PRPLEX",
    0x3E: "VALIDATEPRPL",
    0x13: "PK_VALIDATE_GROUP",
    0x15: "PK_QUIESCE",
    0x16: "PK_GETSET_ADLEVEL",
    0x17: "PK_GETSET_ADLEVEL2",
    0x19: "PK_CLOCKSKEW",
    0x1A: "PK_UUID",
    0x1E: "PK_REGISTER",
    0x28: "PK_PULL_BROKER_ATTRS_REQUEST",
    0x29: "PK_PUSH_BROKER_ATTRS_REQUEST",
    0x2A: "PK_TRUST_REFRESH_REQUEST",
    0x2B: "PK_PULL_BROKER_DOMAIN_INFO",
    0x2C: "PK_CREATE_PRPL",
    0x33: "PK_SET_CERTIFICATE_SAN",
    0x34: "PK_SIGN_CSR_DATA",
    0x35: "PK_AUTH_START_CRL",
    0x36: "PK_CRL_REVOKED",
    0x37: "PK_SIGN_CRL_DATA",
    0x38: "PK_ADD_CERTIFICATE_DISTPOINT",
    0x39: "PK_ADD_LDAP_DOMAIN",
    0x3A: "PK_MODIFY_LDAP_DOMAIN",
    0x3B: "PK_DELETE_LDAP_DOMAIN",
    0x3C: "PK_LIST_LDAP_DOMAIN",
    0x3D: "PK_TEST_LDAP_DOMAIN",
}


class NbatdCommand(Packet):
    fields_desc = [
        IntField("proto_version", 1),
        XIntField("magic", 0xBAADF00D),
        ByteEnumField("msg_type", default=1, enum=NBATD_MSG_TYPES),
        FieldLenField("msg_size", None, length_of="data", fmt=">L"),
        ByteEnumField("unicode_flag", default=1, enum={0: "False", 1: "True"}),
        StrLenField("data", "", length_from=lambda pkt: pkt.msg_size),
    ]


def main():
    p = NbatdCommand()
    p.msg_type = 0x05
    p.data = '<command="Authenticate" username="xxxx-yyyyy-zzzzz-aaaaa" password="redacted" domain="NBU_HOSTS">'
    p.show2()


if __name__ == "__main__":
    main()
