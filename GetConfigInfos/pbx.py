import asyncio
import logging

from utils.network import PBXSocket
from .generic import ScanBaseClass
from .common import ScanState, NbuComponentType


class ListPbxExtensions(ScanBaseClass):
    OPS_PBX_EXTENSIONS = set(
        [
            "CycloneDomainService",
            "InSecCycloneDomainService",
            "opscenter_agent_pd",
            "OPSCENTER_PBXSSLServiceID",
            "SclInsecure",
            "SclInsecure6x",
            "SclSecure6x",
            "SclSecureI",
            "SclSecureIc",
            "SearchBroker",
            "SearchService",
        ]
    )
    PRIMARY_PBX_EXTENSIONS = set(
        [
            "HTTPTUNNEL",
            "TLSPROXY",
            "bpcd",
            "bpdbm",
            "bpdbm-auth-only",
            "bpjobd",
            "bprd",
            "DiscoveryService",
            "DiscoveryService_secsvc",
            "EMM",
            "nbars",
            "nbatd",
            "nbaudit",
            "nbazd",
            "NBDSMFSM",
            "nbevtmgr",
            "NBFSMCLIENT",
            "nbim",
            "nbjm",
            "nbpem",
            "nbrb",
            "NBREM",
            "nbrmms",
            "nbrmms_secsvc",
            "nbsl",
            "nbsl_secsvc",
            "nbstserv",
            "nbsvcmon",
            "nbsvcmon_secsvc",
            "nbvault",
            "vmd",
            "vnetd",
            "vnetd-auth-only",
            "vnetd-no-auth",
            "vnetd-ssa",
        ]
    )
    MEDIA_PBX_EXTENSIONS = set(
        [
            "HTTPTUNNEL",
            "TLSPROXY",
            "bpcd",
            "DiscoveryService",
            "DiscoveryService_secsvc",
            "nbrmms",
            "nbrmms_secsvc",
            "nbsl",
            "nbsl_secsvc",
            "nbsvcmon",
            "nbsvcmon_secsvc",
            "vmd",
            "vnetd",
            "vnetd-auth-only",
            "vnetd-no-auth",
            "vnetd-ssa",
        ]
    )
    CLIENT_PBX_EXTENSIONS = set(
        [
            "bpcd",
            "DiscoveryService",
            "DiscoveryService_secsvc",
            "vnetd",
            "vnetd-auth-only",
            "vnetd-no-auth",
            "vnetd-ssa",
        ]
    )
    PBX_EXTENSIONS = sorted(
        list(
            OPS_PBX_EXTENSIONS
            | PRIMARY_PBX_EXTENSIONS
            | MEDIA_PBX_EXTENSIONS
            | CLIENT_PBX_EXTENSIONS
        ),
        key=str.casefold,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension_states = {}

    def name(self):
        """
        Full name of this scan
        """
        return "PBX_EXCHANGE"

    async def _scan_ext(self, ext: str) -> bool:
        """
        Internal method returning whether an extension was found or not
        """
        async with self._semaphore:
            sock = PBXSocket(self.host, timeout=self.timeout)
            try:
                await sock.connect()
                await sock.handshake(ext)
                await sock.close()
                logging.info(
                    "[ListPbxExtensions] Found accessible extension %s for %s",
                    ext,
                    self.host,
                )
                return True
            except RuntimeError:
                await sock.close()
                return False

    def _guess_role(self) -> NbuComponentType:
        # Build a set of available extensions to compare with those specific to
        # each component
        extensions = set(
            [ext for ext in self.extension_states.keys() if self.extension_states[ext]]
        )

        # First, check if it's an OpsCenter since it has very unique extensions
        ops_unique_exts = self.OPS_PBX_EXTENSIONS - (
            self.PRIMARY_PBX_EXTENSIONS
            | self.MEDIA_PBX_EXTENSIONS
            | self.CLIENT_PBX_EXTENSIONS
        )
        if extensions & ops_unique_exts:
            return NbuComponentType.OPSCENTER

        # Move on to the primary server as it has plenty of unique extensions
        primary_unique_exts = self.PRIMARY_PBX_EXTENSIONS - (
            self.MEDIA_PBX_EXTENSIONS | self.CLIENT_PBX_EXTENSIONS
        )
        if extensions & primary_unique_exts:
            return NbuComponentType.PRIMARY

        # Now, the media server
        media_unique_exts = self.MEDIA_PBX_EXTENSIONS - self.CLIENT_PBX_EXTENSIONS
        if extensions & media_unique_exts:
            return NbuComponentType.MEDIA

        # Finally, at least check some of the client extensions are present
        if extensions & self.CLIENT_PBX_EXTENSIONS:
            return NbuComponentType.CLIENT

        return NbuComponentType.UNKNOWN

    def guess_role(self) -> NbuComponentType:
        """
        Attempt to guess the role of the scanned host based on the discovered
        extensions
        """
        if self.state == ScanState.PENDING:
            raise RuntimeError("The run function has not been called")
        elif self.state == ScanState.RUNNING:
            raise RuntimeError("The scan is not done running")
        return self._guess_role()

    async def _run(self):
        """
        Iterate over all know extensions and check whether they are reachable
        through pbx_exchange or not
        """
        # Reset extension states
        self.extension_states = {ext: False for ext in self.PBX_EXTENSIONS}

        # Run one task for each extension
        tasks = [self._scan_ext(ext) for ext in self.PBX_EXTENSIONS]
        results = await asyncio.gather(*tasks)

        # Populate the dictionary of extensions states
        self.extension_states = {
            self.PBX_EXTENSIONS[i]: results[i] for i in range(len(self.PBX_EXTENSIONS))
        }

    def _text(self) -> str:
        """
        Get a textual representation of the results
        """
        COLUMN_SIZES = (max([len(ext) for ext in self.PBX_EXTENSIONS]), len("[ERROR]"))

        def format_line(ext, status):
            fmt_string = "| {{:<{}}} | {{:<{}}} |".format(*COLUMN_SIZES)
            return fmt_string.format(ext, status)

        out_lines = [
            format_line("EXTENSION", "STATE"),
            format_line(*["-" * n for n in COLUMN_SIZES]),
        ]
        for ext in self.PBX_EXTENSIONS:
            if not self.extension_states[ext] and not self.verbose:
                continue
            status = "[OK]" if self.extension_states[ext] else "[ERROR]"
            out_lines.append(format_line(ext, status))

        out_lines.append("=> Guessed role: " + self.guess_role().value)
        return "\n".join(out_lines)

    def _json(self) -> dict:
        """
        Get a dictionary representation of the results
        """
        return {
            "pbx": {
                "extensions": self.extension_states,
                "guessed_role": self.guess_role().value,
            }
        }
