#!/usr/bin/env python3
import enum
import json
import asyncio
import logging
import argparse

from .vnetd import GetVnetdInfo
from .vxss import TestVxssConfig
from .pbx import ListPbxExtensions
from .api import GetApiInfo


NBU_SCANNERS = [GetVnetdInfo, TestVxssConfig, ListPbxExtensions, GetApiInfo]


class OutputFormat(enum.Enum):
    PLAIN = "plain"
    JSON = "json"


async def scan(
    target: str, nb_threads: int, timeout: int, verbose: bool, out_format: OutputFormat
):
    out = {}
    tasks = {}
    scanners = [
        cls(host=target, nb_threads=nb_threads, timeout=timeout, verbose=verbose)
        for cls in NBU_SCANNERS
    ]

    def callback(task):
        scanner = tasks[task]
        if out_format == OutputFormat.PLAIN:
            print("---", scanner.name(), "Scan Results:")
            print(scanner.text())

    async with asyncio.TaskGroup() as tg:
        for scanner in scanners:
            scanner.scanners = scanners
            task = tg.create_task(scanner.run())
            tasks[task] = scanner
            task.add_done_callback(callback)

    if out_format == OutputFormat.JSON:
        for scanner in scanners:
            out |= scanner.json()
    return out


def main():
    parser = argparse.ArgumentParser(description="NetBackup scanner tool")

    parser.add_argument("targets", nargs="*", help="Target hosts")
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=5,
        help="Maximum number of concurrent jobs",
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
        help="Run in quiet mode",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-l",
        "--log-level",
        help="Define the log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=10, help="Timeout for TCP connections"
    )
    parser.add_argument(
        "-f",
        "--format",
        help="Output format",
        choices=[e.value for e in OutputFormat],
        default="plain",
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input file containing the list of hosts to scan",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file",
    )

    args = parser.parse_args()

    # Start by setting up logging
    if args.verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.getLogger().setLevel(args.log_level)

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

    # Check whether the number of jobs is reasonable
    if args.jobs > 20:
        logging.warn(
            """Running with a high number of concurrent jobs may yield incorrect results!
            pbx_exchange is not designed to handle high numbers of clients and could return false positives/negatives"""
        )

    # Check where and how to write the output
    out_format = OutputFormat(args.format)
    if args.output and out_format == OutputFormat.PLAIN:
        logging.error("--output option is not supported with plaintext format")
        exit(1)

    # Actually perform the scan
    out_dict = {}
    for i, target in enumerate(targets):
        if out_format == OutputFormat.PLAIN:
            if i > 0:
                print("\n\n", end="")
            print(f"[nbuscan results for {target}]")

        verbose = logging.getLogger().getEffectiveLevel() < logging.WARNING
        out_dict[target] = asyncio.run(
            scan(target, args.jobs, args.timeout, verbose, out_format)
        )

    # Write the output if it wasn't already done during the scan
    if out_format == OutputFormat.JSON:
        if args.output:
            with open(args.output, "w") as f:
                json.dump(out_dict, f)
        else:
            print(json.dumps(out_dict, indent=2))


if __name__ == "__main__":
    main()
