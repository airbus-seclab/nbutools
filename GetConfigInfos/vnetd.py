import logging

from utils.network import VNETDSocket
from .generic import ScanBaseClass


class GetVnetdInfo(ScanBaseClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nbu_version = "Unknown"
        self.primary_server = "Unknown"

    def name(self):
        """
        Full name of this scan
        """
        return "VNETD"

    async def _run(self):
        """
        Attempt to connect to vnetd and fetch information
        """
        # Reset gathered info
        self.nbu_version = "Unknown"
        self.primary_server = "Unknown"

        # Open a socket to vnetd using pbx_exchange or, if that fails, through
        # the assigned vnetd port
        try:
            sock = VNETDSocket(self.host, use_pbx=True, timeout=self.timeout)
            await sock.connect()
        except:
            sock = VNETDSocket(self.host, use_pbx=False, timeout=self.timeout)
            await sock.connect()

        # Perform the initial handshake with vnetd, which is necessary before
        # issuing any command
        await sock.handshake()

        # Send the commands to get the information we can
        self.nbu_version = await sock.get_version() or self.nbu_version
        self.primary_server = await sock.get_primary_server() or self.primary_server

        # Cleanup
        await sock.close()

    def _text(self) -> str:
        """
        Get a textual representation of the results
        """
        return "Running NetBackup version {}\nAssigned Primary Server: {}".format(
            self.nbu_version, self.primary_server
        )

    def _json(self) -> dict:
        """
        Get a dictionary representation of the results
        """
        return {
            "vnetd": {
                "version": self.nbu_version,
                "primary-server": self.primary_server,
            }
        }
