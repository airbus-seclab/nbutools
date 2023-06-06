#!/usr/bin/python3
import codecs
import logging


class ParseFilesHelper(object):
    """ParseFilesHelper"""

    def __init__(self, yekcnedwssap_filepath, vxdbms_filepath):
        self.RECORD_LEN = 268
        self.KEY_OFF = 0x89
        self.TAG_OFF = 0x08
        self.yekcnedwssap = yekcnedwssap_filepath
        self.vxdbmsconf = vxdbms_filepath

    def find_current_encryptionkey(self):
        try:
            with open(self.yekcnedwssap, "rb") as f:
                with open(self.vxdbmsconf, "r") as conf:
                    yekcnedwssapbytes = f.read()
                    if len(yekcnedwssapbytes) % self.RECORD_LEN != 0:
                        logging.error(
                            "Wrong file format for encryption key (%s): unexpected length",
                            self.yekcnedwssap,
                        )
                        return None

                    confstr = conf.read()
                    records = {}
                    for i in range(0, int(len(yekcnedwssapbytes) / self.RECORD_LEN)):
                        raw = yekcnedwssapbytes[
                            i * self.RECORD_LEN : i * self.RECORD_LEN
                            + self.RECORD_LEN
                            - 1
                        ]
                        tag = codecs.encode(
                            raw[self.TAG_OFF : self.KEY_OFF - 1].rstrip(b"\x00"), "hex"
                        ).decode()
                        key = codecs.encode(
                            raw[self.KEY_OFF :].rstrip(b"\x00"), "hex"
                        ).decode()
                        records[tag] = key

                for i in records:
                    if i in confstr:
                        logging.debug("TAG found. corresponding key: %s", records[i])
                        return records[i]

                logging.error(
                    "No TAG found in both configuration file %s and encryption key file %s",
                    self.vxdbmsconf,
                    self.yekcnedwssap,
                )
                return None
        except (FileNotFoundError, UnicodeDecodeError) as e:
            logging.error("File not found or with wrong format, parsing aborted: %s", e)
            return None

    def find_current_VXDBMS_NB_PASSWORD(self):
        try:
            with open(self.vxdbmsconf, "r") as f:
                vxdbmsconf = f.readlines()
                for l in vxdbmsconf:
                    if "VXDBMS_NB_PASSWORD" in l:
                        pwd = l.split(":")[1][:-4]
                        return pwd
                return None
        except (FileNotFoundError, UnicodeDecodeError):
            print("[DEBUG] File not found or with wrong format. Parsing aborted.")
            return None


def test(yekcnedwssap_path, vxdbmsconf_path):
    filehlpr = ParseFilesHelper(yekcnedwssap_path, vxdbmsconf_path)
    key = filehlpr.find_current_encryptionkey()
    pwd = filehlpr.find_current_VXDBMS_NB_PASSWORD()
    if key and pwd:
        print("Files have been parsed correctly:")
        print("- Pwd: " + pwd)
        print("- Key: " + key)


if __name__ == "__main__":
    test("tests/.yekcnedwssap", "tests/vxd.conf")
    test("tests/nofile", "tests/vxd.conf")
    test("tests/.yekcnedwssap", "tests/.yekcnedwssap")
    test("tests/vxd.conf", "tests/vxd.conf")
