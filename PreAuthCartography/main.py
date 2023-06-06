#!/usr/bin/python3
import asyncio
import argparse
import logging
from io import StringIO

import requests
from lxml import etree

from tabulate import tabulate

from GetConfigInfos.vnetd import GetVnetdInfo
from GetConfigInfos.pbx import ListPbxExtensions
from GetConfigInfos.common import ScanState
from .plotNetbackup import *

import urllib3
urllib3.disable_warnings()


class NetbackupServer(object):
    def __init__(self, ip):
        self.ip = ip

    def connect(self):
        self.vnetd = GetVnetdInfo(self.ip)
        asyncio.run(self.vnetd.run())
        return self.vnetd.state

    def get_version(self):
        try:
            version = self.vnetd.json()["vnetd"]["version"]
            logging.info("Found version %s for %s", version, self.ip)
            return version
        except Exception:
            logging.warning("Got no version information for %s", self.ip)
            return "Unknown"

    def get_ops_version(self):
        page = requests.get("https://" + self.ip + "/opscenter", verify=False)
        tree = etree.parse(
            StringIO(page.content.decode("utf-8")), parser=etree.HTMLParser()
        )

        version = ""
        for i in tree.getroot():
            if i.tag == "body":
                for j in i:
                    # print(j.attrib, j.keys())
                    if ("class" in j.keys()) and (j.attrib["class"] == "wrapper"):
                        for t in j:
                            if t.attrib["class"] == "productname":
                                version = (
                                    t[0].text.split(" ")[1].replace(".", "") + "0000"
                                )
                                break

        logging.info("Found version %s for %s", version, self.ip)
        return version

    def get_master(self):
        try:
            master_server = self.vnetd.json()["vnetd"]["primary-server"]
            logging.info("Found primary server %s for %s", master_server, self.ip)
        except:
            logging.info("Got no primary server information for %s", self.ip)
            return "Unknown"

        if master_server:
            return master_server
        else:
            logging.warning("Unable to find master server for %s", self.ip)
            return "Unknown"

    def get_type(self):
        logging.info("Starting pbx scan for %s", self.ip)
        pbx = ListPbxExtensions(self.ip)
        asyncio.run(pbx.run())
        return pbx.guess_role()

    def get_info(self):
        try:
            nature = self.get_type()
        except Exception as e:
            logging.warning("Failed to guess role for %s: %s", self.ip, e)
            nature = NbuComponentType.UNKNOWN

        if nature == NbuComponentType.OPSCENTER:
            return [nature, self.get_ops_version(), "-", "-"]

        connect_error = self.connect()
        if connect_error != ScanState.SUCCESS:
            if not nature:
                return [NbuComponentType.UNKNOWN, "Unknown", "Unknown", "down"]
            else:
                return [nature, "Unknown", "Unknown", "down"]
        else:
            return [nature, self.get_version(), self.get_master(), "up"]


class NetbackupInfra(object):
    def __init__(self, servers, output, noout=False, plot=""):
        self.to_scan = servers
        self.servers_scanned = {}
        self.output = output
        self.noout = noout
        self.plot = plot

    def init(self):
        try:
            with open(self.output, "r") as f:
                logging.warning("Using cached data from %s", self.output)
                for line in f.readlines():
                    line = line.strip().split(";")
                    s, v = line[0], [
                        NbuComponentType(line[1]),
                        line[2],
                        line[3],
                        line[4],
                    ]
                    self.servers_scanned[s] = v
        except FileNotFoundError:
            pass

    def run(self):
        self.init()
        while len(self.to_scan) != 0:
            server = self.to_scan.pop(0)
            if self.need_scan(server):
                self.scan(server)
                master = self.servers_scanned[server][2]
                if master != "Unknown" and master != "-" and self.need_scan(master):
                    logging.info("Discovered new server to scan: %r", master)
                    self.to_scan.append(master)
        if not (self.noout):
            self.print()
        if self.plot:
            self.plotter()
        self.store()

    def need_scan(self, server):
        if server:
            return not server in self.to_scan and not server in self.servers_scanned
        else:
            return 0

    def scan(self, server):
        logging.info("Starting scan for server %s", server)
        nb = NetbackupServer(server)
        self.servers_scanned[server] = nb.get_info()

    def result(self):
        s = []
        for server, values in self.servers_scanned.items():
            s.append(f"{server};{values[0].value};{values[1]};{values[2]};{values[3]}")
        return s

    def store(self):
        with open(self.output, "w") as f:
            f.write("\n".join(self.result()))

    def print(self):
        tab = [["Machines", "Type", "Version", "Master", "Vnetd State"]]
        for r in self.result():
            tab.append(r.split(";"))
        print(tabulate(tab, headers="firstrow", tablefmt="grid"))

    def plotter(self):
        dotgraph = generate_dotgraph(self.result())
        dotgraph.format = "png"
        dotgraph.render(self.plot.split(".")[0], cleanup=True)
        return 0

    def get_server_result(self, server):
        return f"{server};{self.servers_scanned[server][0].value};{self.servers_scanned[server][1]};{self.servers_scanned[server][2]};{self.servers_scanned[server][3]}"


def parse_args():
    parser = argparse.ArgumentParser(description="NetBackup infrastructure scanner")
    parser.add_argument("targets", nargs="*", help="Target hosts")
    parser.add_argument(
        "-i",
        "--input",
        help="Input file containing the list of hosts to scan",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Run in verbose mode",
        action="count",
        default=0,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Disable output on stdout",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-o",
        "--output",
        default="netbackup_infra.csv",
        help="CSV File output",
    )
    parser.add_argument(
        "--plot",
        default="netbackup_infra_map.png",
        help="Infrastructure map file output path",
    )
    return parser, parser.parse_args()


def main():
    parser, args = parse_args()

    # Start by setting up logging
    if args.verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    # Get targets
    targets = []
    if args.input:
        with open(args.input, "r") as f:
            targets = f.readlines()

        # Cleanup lines
        targets = map(str.strip, targets)
        targets = filter(lambda l: bool(l), targets)
        targets = list(targets)

    targets += args.targets
    if not targets:
        parser.print_help()
        exit(1)

    nb = NetbackupInfra(targets, output=args.output, noout=args.quiet, plot=args.plot)
    nb.run()

    return 0


if __name__ == "__main__":
    main()
