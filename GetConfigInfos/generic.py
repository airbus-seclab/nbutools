import abc
import asyncio
import logging

from .common import ScanState, NbuComponentType


class ScanBaseClass(abc.ABC):
    # This can be used to limit on which component a scan should run
    _SCANNABLE_COMPONENTS = set(NbuComponentType)

    def __init__(self, host, nb_threads=1, timeout=5, verbose=False, scanners=[]):
        self.host = host
        self.nb_threads = nb_threads
        self.timeout = timeout
        self.verbose = verbose
        self.scanners = scanners

        self._state = ScanState.PENDING
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()
        self._semaphore = asyncio.Semaphore(value=self.nb_threads)

    ### Helper methods

    async def _component_type(self) -> NbuComponentType:
        """
        Return the guessed role of the target of this scanner
        This will rely on the ListPbxExtensions scanner. If it was not been run
        (yet), it will wait for the result before moving on
        """
        # Build a list of scanners able to guess the target's role
        scanners = (s for s in self.scanners if hasattr(s, "guess_role"))

        for pbx_scanner in scanners:
            # Check whether this scanner has already run
            if pbx_scanner.state == ScanState.ERROR:
                raise RuntimeError("ListPbxExtensions failed")
            if pbx_scanner.state == ScanState.SKIPPED:
                raise RuntimeError("ListPbxExtensions was skipped")
            elif pbx_scanner.state != ScanState.SUCCESS:
                # If it hasn't run, run it or wait for it to be done running
                await pbx_scanner.run()
                break
        else:
            raise RuntimeError("No ListPbxExtensions scanner found")

        # Check the guessed role of the target
        return pbx_scanner.guess_role()

    ### Wrappers handling state

    @property
    def state(self) -> ScanState:
        """
        Current state of this scanner
        """
        return self._state

    async def run(self):
        """
        Run this scanner, updating its state and triggering a finish event
        If it is already running, simply wait for it to finish
        """
        if self._state == ScanState.RUNNING:
            # If the scan is already running, simply wait for it to finish
            await self._event.wait()
            return

        self._state = ScanState.RUNNING
        self._event.clear()
        try:
            if await self.skip():
                logging.info("Skipping %s scan", self.name())
                self._state = ScanState.SKIPPED
            else:
                logging.info("Starting %s scan", self.name())
                await self._run()
                self._state = ScanState.SUCCESS
        except Exception as e:
            self._state = ScanState.ERROR
            logging.warn("%s scanner failed with error: %s", self.name(), e)
        finally:
            self._event.set()

    async def skip(self) -> bool:
        """
        Check whether this scan should be skipped or not
        """
        # If every type of component can be scanned, never skip this
        if self._SCANNABLE_COMPONENTS == set(NbuComponentType):
            return False

        # If this scan is restricted to only specific components, wait to know
        # which component type we are dealing with
        try:
            component = await self._component_type()
            return component not in self._SCANNABLE_COMPONENTS
        except RuntimeError as e:
            logging.info("Failed to guess target role: %s", e)
            return True

    def text(self) -> str:
        """
        Get a textual representation of the results
        """
        if self._state == ScanState.PENDING:
            raise RuntimeError("The run function has not been called")
        elif self._state == ScanState.RUNNING:
            raise RuntimeError("The scan is not done running")
        elif self._state == ScanState.SKIPPED:
            return "Skipped"

        return self._text()

    def json(self) -> dict:
        """
        Get a JSON representation of the results
        """
        if self._state == ScanState.PENDING:
            raise RuntimeError("The run function has not been called")
        elif self._state == ScanState.RUNNING:
            raise RuntimeError("The scan is not done running")

        return self._json()

    ### Methods to override

    @abc.abstractmethod
    def name(self) -> str:
        """
        Full name of this scan
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def _run(self):
        """
        Actually run the scan
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _text(self, verbose: bool) -> str:
        """
        Get a textual representation of the results
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _json(self) -> dict:
        """
        Get a JSON representation of the results
        """
        raise NotImplementedError()
