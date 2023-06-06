#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import graphviz
from GetConfigInfos.common import NbuComponentType

OFF_NAME = 0
OFF_TYPE = 1
OFF_VERS = 2
OFF_MAST = 3
OFF_VNET = 4

type_colors = {  # [fill, border/font]
    NbuComponentType.OPSCENTER: ["#ffe6ccff", "#d79b00"],
    NbuComponentType.PRIMARY: ["#d5e8d4", "#82b366"],
    NbuComponentType.MEDIA: ["#f8ceccff", "#b85450"],
    NbuComponentType.CLIENT: ["#dae8fcff", "#6c8ebf"],
    NbuComponentType.UNKNOWN: ["white", "gray"],
}

version_colors = {
    "750000": "firebrick4",
    "760000": "brown3",
    "800000": "chocolate3",
    "810000": "gold",
    "820000": "darkgreen",
    "unknown": "gray",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Plotter of Netbackup infra")
    parser.add_argument("servers", metavar="PATH", nargs="?")
    return parser.parse_args()


def get_nodes(s):
    l = []
    for i in s.body:
        l.append(i.split(" ")[0][1:])
    # print(l)
    return l


def generate_component(s, component):
    if '"' + component[OFF_NAME] + '"' not in get_nodes(s):
        s.attr(
            "node",
            shape="Mrecord",
            style="filled",
            fillcolor=type_colors.get(component[OFF_TYPE])[0],
            color=type_colors.get(component[OFF_TYPE])[1],
            fontcolor=type_colors.get(component[OFF_TYPE])[1],
        )
        s.node(
            component[OFF_NAME],
            label=component[OFF_NAME] + "|" + component[OFF_TYPE].value,
            rankdir="TB",
        )
        s.edge(
            component[OFF_NAME] + ":s",
            component[OFF_NAME] + ":s",
            style="dotted",
            rankdir="LR",
            arrowhead="dot",
            arrowsize="1.3",
            maxlen=".1",
            color="invis",
            headlabel=component[OFF_VERS],
            fontsize="7",
            fontcolor=version_colors.get(component[OFF_VERS]),
            labeldistance="2",
            fillcolor=version_colors.get(component[OFF_VERS]),
        )


def generate_link(s, component):
    generate_component(
        s,
        [
            component[OFF_MAST],
            NbuComponentType.UNKNOWN,
            "unknown",
            "unknown",
            "unknown",
        ],
    )
    s.attr(
        "edge",
        color=type_colors.get(component[OFF_TYPE])[1],
        arrowhead="none",
    )
    s.edge(component[OFF_NAME], component[OFF_MAST])


def generate_legend(s):
    with s.subgraph(name="legend") as c:
        for v in version_colors:
            c.attr(
                "node",
                shape="none",
                style="filled",
                fillcolor="white",
                fontcolor="black",
            )
            c.node(v, v)
            c.edge(v, version_colors.get(v), style="invis", color="white")

            c.attr(
                "node",
                shape="point",
                style="filled",
                width=".15",
                color=version_colors.get(v),
                fillcolor=version_colors.get(v),
                margin="0,0",
                height="0.5",
            )
            c.node(version_colors.get(v), "")

        c.attr(style="filled", bcolor="lightgrey", mindist="0.1")


def generate_dotgraph(servers):
    s = graphviz.Digraph("G")
    s.attr(rankdir="LR")

    # creation of boxes for each identified component
    for line in servers:
        line = line.split(";")
        line = [line[0], NbuComponentType(line[1]), line[2], line[3], line[4]]
        generate_component(s, line)

    # creation of links
    for line in servers:
        line = line.split(";")
        line = [line[0], NbuComponentType(line[1]), line[2], line[3], line[4]]
        if line[OFF_MAST] != "Unknown" and line[OFF_TYPE] != NbuComponentType.OPSCENTER:
            generate_link(s, line)

    # generate_legend(s)

    return s


def main():
    args = parse_args()
    with open(args.servers, "r") as f:
        servers = list(map(lambda p: p.lower(), f.readlines()))
        print(generate_dotgraph(servers))

    return 0


if __name__ == "__main__":
    sys.exit(main())
