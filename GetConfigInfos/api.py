import json
import asyncio
import logging
import aiohttp

from .generic import ScanBaseClass
from .common import NbuComponentType


class GetApiInfo(ScanBaseClass):
    # This scan should only run if the target is a primary server
    _SCANNABLE_COMPONENTS = {NbuComponentType.PRIMARY}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_info = {}

    def name(self):
        """
        Full name of this scan
        """
        return "NETBACKUP_API"

    def _api_url(self) -> str:
        return f"https://{self.host}:1556/netbackup"

    async def _fetch_data(self, client, url) -> bytes:
        async with self._semaphore:
            try:
                logging.debug(
                    "[GetApiInfo] Attempting to fetch information from API at %s", url
                )
                async with client.get(
                    url, verify_ssl=False, timeout=self.timeout
                ) as res:
                    res.raise_for_status()
                    data = await res.text()
                    logging.debug("[GetApiInfo] Got response from %s: %s", url, data)
                    return data
            except TimeoutError:
                logging.warning(
                    "[GetApiInfo] Timed out while connecting API from %s", url
                )
                return b""
            except aiohttp.ClientError as e:
                logging.warning(
                    "[GetApiInfo] Failed to get API info from %s: %s", url, e
                )
                return b""

    async def _fetch_json(self, client, url) -> dict:
        data = await self._fetch_data(client, url)
        if not data:
            return {}

        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError as e:
            logging.warning("[GetApiInfo] Failed to parse API data from %s: %s", url, e)
            return {}

    async def _get_api_info(self) -> dict:
        """
        See https://sort.veritas.com/public/documents/nbu/10.1/windowsandunix/productguides/html/gateway
        """
        base_url = self._api_url()
        async with aiohttp.ClientSession() as client:
            results = await asyncio.gather(
                self._fetch_data(client, f"{base_url}/tokenkey"),
                # self._fetch_data(client, f"{base_url}/ping"),
            )
        return {
            "jwt-key": results.pop(0).decode("utf-8"),
            # "ping": results.pop(0).decode("utf-8"),
        }

    async def _get_security_info(self) -> dict:
        """
        See https://sort.veritas.com/public/documents/nbu/10.1/windowsandunix/productguides/html/security
        """
        base_url = f"{self._api_url()}/security"

        async with aiohttp.ClientSession() as client:
            results = await asyncio.gather(
                # self._fetch_json(client, f"{base_url}/cacert"),
                # self._fetch_data(client, f"{base_url}/certificates/crl"),
                self._fetch_json(client, f"{base_url}/properties"),
                # self._fetch_json(client, f"{base_url}/properties/default"),
                # self._fetch_data(client, f"{base_url}/ping"),
                self._fetch_json(client, f"{base_url}/servertime"),
                self._fetch_json(client, f"{base_url}/serverinfo"),
            )
        return {
            # "cacert": results.pop(0),
            # "crl": results.pop(0).hex(),
            "properties": results.pop(0),
            # "properties-default": results.pop(0),
            # "ping": results.pop(0).decode("utf-8"),
            "servertime": results.pop(0),
            "serverinfo": results.pop(0),
        }

    async def _run(self):
        """
        Attempt to connect to the Primary Server API and obtain information
        """
        # Reset gathered info
        self.api_info = {}

        # Poll pre-auth API endpoints for information
        results = await asyncio.gather(
            # self._get_api_info()
            self._get_security_info()
        )

        # self.api_info["api"] = results.pop(0)
        self.api_info["security"] = results.pop(0)

    def _text(self) -> str:
        """
        Get a textual representation of the results
        """
        out_lines = []

        security_info = self.api_info.get("security", {})
        server_info = security_info.get("serverinfo")
        if server_info:
            # Extract most important information from the whole dict
            out_lines.append(f"Server Name: {server_info.get('serverName', 'Unknown')}")
            out_lines.append(f"Host ID: {server_info.get('masterHostId', 'Unknown')}")
            out_lines.append(
                f"NetBackup version: {server_info.get('nbuVersion', 'Unknown')}"
            )
            out_lines.append(f"SSO enabled: {server_info.get('ssoEnabled', 'Unknown')}")

        security_properties = security_info.get("properties")
        if security_properties:
            # Extract most important information from the whole dict
            # First, whether TLS is used
            secure_comms = security_properties["allowInsecureBackLevelHost"]
            state = "Enabled" if secure_comms else "Disabled"
            out_lines.append(f"Secure Communications: {state}")

            # Second, how certificates are deployed
            cert_deploy_level = security_properties["certificateAutoDeployLevel"]
            if cert_deploy_level == 0:
                state = "Very high"
            elif cert_deploy_level == 1:
                state = "High"
            elif cert_deploy_level == 2:
                state = "Medium"
            else:
                state = "Unknown"
            out_lines.append(f"Certificate auto-deployment level: {state}")

        return "\n".join(out_lines)

    def _json(self) -> dict:
        """
        Get a dictionary representation of the results
        """
        return {
            "api": self.api_info,
        }
