from scapy import *
from scapy.packet import *
from scapy.fields import *


PBX_MSG_TYPES = {
    0x0101: "INIT",
    0x0102: "CON",
    0x0106: "RDV",
    0x0300: "ACK",
}


class PbxRegister(Packet):
    fields_desc = [
        ByteField("proto_version", 4),
        ShortEnumField(
            "msg_type",
            0x0101,
            PBX_MSG_TYPES,
        ),
        ByteField("client_state", 4),
        FieldLenField("msg_size", None, length_of="data", fmt=">L"),
        ByteField("error_code", 0),
        XStrFixedLenField("rand", default=0, length=7),
        StrLenField("data", "", length_from=lambda pkt: pkt.msg_size),
    ]


def main():
    b = PbxRegister(
        bytes.fromhex(
            "0401010400000085000000000000000073737469630000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007573657200"
        )
    )
    b.show2()


if __name__ == "__main__":
    main()
