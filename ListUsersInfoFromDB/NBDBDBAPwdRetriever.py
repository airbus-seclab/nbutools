#!/usr/bin/python3
import codecs
import logging

from Crypto.Cipher import AES
from Crypto.Util import Counter


class NBDBDBAPwdRetriever(object):
    """NBDBDBAPwdRetriever"""

    def __init__(self, yekkey):  # yekkey format: hexa string
        self.AES_256_IV_SZ = 32
        self.key = codecs.decode(yekkey, "hex")

    def decrypt_nbdb_dba_password(self, vxdbmsnb_password):
        logging.debug("Attempting to decrypt DBA password %s", vxdbmsnb_password)

        iv = codecs.decode(vxdbmsnb_password[: self.AES_256_IV_SZ], "hex")
        encpwd = codecs.decode(vxdbmsnb_password[self.AES_256_IV_SZ :], "hex")
        ctr = Counter.new(128, initial_value=int.from_bytes(iv, "big"))

        aes = AES.new(self.key, AES.MODE_CTR, counter=ctr)
        pwd = aes.decrypt(encpwd)

        logging.debug("Decrypted DBA password: %s", pwd)
        return pwd


def test():
    pwd = "a18a56ec761ad234ba1549712ba53c4ada3228badb5f"
    key = "d2a3ee736aafa29bf997f1c355c8b2da279fb00ca879997bc69d31acc2bb9f23"

    pwd_retriever = NBDBDBAPwdRetriever(key)
    dbapwd = pwd_retriever.decrypt_nbdb_dba_password(pwd)
    print(codecs.decode(dbapwd))


if __name__ == "__main__":
    test()
