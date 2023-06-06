import logging

from utils.network import VNETDSocket
from .generic import ScanBaseClass


class TestVxssConfig(ScanBaseClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vxss_info = None

    def name(self):
        """
        Full name of this scan
        """
        return "VXSS"

    USE_VXSS_MAP = {
        0: "AUTOMATIC",
        1: "REQUIRED",
        2: "PROHIBITED",
    }

    AUTHENTICATION_MAP = {
        0: "OFF",
        1: "ON",
    }

    AUTHORIZATION_MECHANISM_MAP = {
        0: "NIS",
        1: "NIS+",
        2: "PASSWD",
        3: "VXPD",
        4: "WINDOWS",
    }

    def _prettify(self, d, k, m):
        v = d.get(k, None)
        try:
            d[k] = m[int(v)]
        except (ValueError, KeyError):
            return v
        except TypeError:
            return "Unknown"

    async def _run(self):
        """
        Attempt to connect to vnetd and fetch information about VxSS
        """
        # Reset gathered info
        self.vxss_info = None

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

        # Send the command to get the information we can
        self.vxss_info = await sock.get_security_info()

        if self.vxss_info:
            # "Translate" some fields into readable information
            self._prettify(self.vxss_info, "USE_VXSS", self.USE_VXSS_MAP)
            self._prettify(
                self.vxss_info, "USE_AUTHENTICATION", self.AUTHENTICATION_MAP
            )

            for domain in self.vxss_info["AUTHENTICATION_DOMAIN"]:
                self._prettify(domain, "mechanism", self.AUTHORIZATION_MECHANISM_MAP)

            for network in self.vxss_info["VXSS_NETWORK"]:
                self._prettify(network, "use_vxss", self.USE_VXSS_MAP)
        else:
            logging.warning("[TestVxssConfig] Failed to get security info from vnetd")

        # Cleanup
        await sock.close()

    def _text(self) -> str:
        """
        Get a textual representation of the results
        """
        if not self.vxss_info:
            return "No information"

        # Attempt to reproduce the format of bp.conf
        out_lines = []
        out_lines.append("USE_VXSS = {}".format(self.vxss_info["USE_VXSS"]))
        for network in self.vxss_info["VXSS_NETWORK"]:
            out_lines.append(
                "VXSS_NETWORK = {} {}".format(
                    network["network"],
                    network["use_vxss"],
                )
            )

        out_lines.append(
            "USE_AUTHENTICATION = {}".format(self.vxss_info["USE_AUTHENTICATION"])
        )
        for domain in self.vxss_info["AUTHENTICATION_DOMAIN"]:
            out_lines.append(
                'AUTHENTICATION_DOMAIN = {} "{}" {} {} {}'.format(
                    domain["domain"],
                    domain["comment"],
                    domain["mechanism"],
                    domain["broker"],
                    domain["port"],
                )
            )

        return "\n".join(out_lines)

    def _json(self) -> dict:
        """
        Get a dictionary representation of the results
        """
        return {"vxss": self.vxss_info}
