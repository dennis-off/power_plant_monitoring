import logging
import random
import sys
import threading
import time
from abc import ABC, abstractmethod
from enum import Enum

_logger = logging.getLogger(__name__)

class ProgramState(Enum):
    IDLE = 1
    RUNNING = 2
    STOPPING = 3


class ExecutionMode(Enum):
    BLOCKING = 1
    NONBLOCKING = 2


class ProgramThreadError(Exception):
    pass


class ProgramThread(ABC):
    def __init__(self, name: str):

        self._name: str = name

        self._state_lock: threading.Lock = threading.Lock()

        self._ct: threading.Event = None

        self._workerThread: threading.Thread = None

        self._thread_done: threading.Event = threading.Event()

        self._state: ProgramState = ProgramState.IDLE

        self._last_exception: Exception = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value != self._state:
            _logger.info(
                f"({self.name}) State changed: Prev. state = {self._state}, New state = {value}"
            )
            self._state = value

    @property
    def is_running(self):
        return self._state != ProgramState.IDLE

    @property
    def last_exception(self):
        return self._last_exception

    @last_exception.setter
    def last_exception(self, value):
        if value != self._last_exception:
            self._last_exception = value

    def _update_state(self, newState: ProgramState):
        # oldState = self.state
        self.state = newState

    def _start_impl(self, executionMode: ExecutionMode, externalToken: threading.Event):

        if self.is_running:
            raise ProgramThreadError(
                f"({self.name}) Thread {self.name} already running"
            )

        _logger.info(f"({self.name}) Starting Thread {self.name}")

        self._prepare_internal()

        if externalToken is not None:
            self._ct = externalToken
        else:
            self._ct = threading.Event()

        self._thread_done.clear()

        if executionMode == ExecutionMode.BLOCKING:
            self.run(self._ct)
        elif executionMode == ExecutionMode.NONBLOCKING:
            self._workerThread = threading.Thread(
                target=self.run, name=self.name, args=(self._ct,)
            )

            self._workerThread.start()

    def start_blocking(self, externalToken: threading.Event):
        self._start_impl(ExecutionMode.BLOCKING, externalToken)

    def start(self, externalToken: threading.Event = None):
        with self._state_lock:
            self._start_impl(ExecutionMode.NONBLOCKING, externalToken)

    def stop(self):
        with self._state_lock:
            if self.state == ProgramState.RUNNING:
                _logger.info(f"({self.name}) Stopping thread {self.name}")

                self._update_state(ProgramState.STOPPING)

                if self._ct is not None:
                    self._ct.set()

    def run(self, ct: threading.Event):

        try:
            self.last_exception = None

            self._update_state(ProgramState.RUNNING)

            self._run_internal(self._ct)

            if self._ct.is_set():
                finalMsg = f"({self.name}) Thread '{self.name}' was aborted by user."
                _logger.info(finalMsg)

        except Exception as ex:

            if self._ct.is_set():
                finalMsg = f"({self.name}) Thread '{self.name}' was aborted by user."
                _logger.info(finalMsg)
            else:
                finalMsg = f"({self.name}) Thread Error in '{self.name}': {ex}"
                _logger.error(finalMsg)

            self._last_exception = ex
        finally:
            try:
                self._stop_internal()
                _logger.info(f"({self.name}) Thread {self.name} stopped")
            finally:
                self._update_state(ProgramState.IDLE)
                self._thread_done.set()

                self._finally_internal()

    @abstractmethod
    def _run_internal(self, ct: threading.Event):
        pass

    def _prepare_internal(self):
        pass

    def _stop_internal(fself, finalMessage: str = ""):
        pass

    def _finally_internal(self):
        pass
