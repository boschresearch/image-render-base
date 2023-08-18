#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Author: Christian Perwass (CR/ADI2.1)
# <LICENSE id="Apache-2.0">
#
#   Image-Render Base Functions module
#   Copyright 2023 Robert Bosch GmbH and its subsidiaries
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# </LICENSE>
###

import time
import enum
import threading
import queue

from .cls_process_handler import CProcessHandler
from .cls_process_output import CProcessOutput


class EProcessStatus(enum.Enum):
    NOT_STARTED = enum.auto()
    STARTING = enum.auto()
    RUNNING = enum.auto()
    ENDED = enum.auto()
    TERMINATED = enum.auto()


# endclass


class CProcessGroupHandler:
    def __init__(self):
        self._qProcStdOut: queue.Queue = queue.Queue()
        self._lockProcData: threading.Lock = threading.Lock()

        self._dicProcOutput: dict[int, CProcessOutput] = dict()
        self._dicProcStatus: dict[int, EProcessStatus] = dict()
        self._dicProcTerminateEvent: dict[int, threading.Event] = dict()

        self._setProcStatusChanged: set[int] = set()
        self._setProcOutputChanged: set[int] = set()

    # enddef

    # ##################################################################################################
    def Clear(self, *, bForce: bool = False):
        if bForce is False and not self.AllEnded():
            raise RuntimeError("Cannot clear while processes are running")
        # endif

        self._dicProcOutput = dict()
        self._dicProcStatus = dict()
        self._dicProcTerminateEvent = dict()
        self._setProcOutputChanged = set()
        self._setProcStatusChanged = set()

    # enddef

    # ##################################################################################################
    def AllEnded(self) -> bool:
        with self._lockProcData:
            eStatus: EProcessStatus = None
            for eStatus in self._dicProcStatus.values():
                if eStatus != EProcessStatus.ENDED and eStatus != EProcessStatus.TERMINATED:
                    return False
                # endif
            # endfor
        # endwith

        return True

    # enddef

    # ##################################################################################################
    def AddProcessHandler(self, *, _iJobId: int, _xProcHandler: CProcessHandler):
        if _iJobId in self._dicProcStatus:
            raise RuntimeError(f"Job Id '{_iJobId}' already used")
        # endif

        self._dicProcTerminateEvent[_iJobId] = threading.Event()

        _xProcHandler.AddHandlerPreStart(self._CreateCallback_ProcStarting(_iJobId))
        _xProcHandler.AddHandlerPostStart(self._CreateCallback_ProcStarted(_iJobId))
        _xProcHandler.AddHandlerEnded(self._CreateCallback_ProcEnded(_iJobId))
        _xProcHandler.AddHandlerStdOut(self._CreateCallback_ProcStdOut(_iJobId))
        _xProcHandler.AddHandlerPollTerminate(self._CreateCallback_ProcPollTerminate(_iJobId))
        self._dicProcOutput[_iJobId] = CProcessOutput()
        self._dicProcStatus[_iJobId] = EProcessStatus.NOT_STARTED

    # enddef

    # ##################################################################################################
    def GetProcStatus(self, iId: int) -> EProcessStatus:
        with self._lockProcData:
            return self._dicProcStatus.get(iId)
        # endwith

    # enddef

    # ##################################################################################################
    def GetProcOutput(self, iId: int) -> CProcessOutput:
        return self._dicProcOutput.get(iId)

    # enddef

    # ##################################################################################################
    def GetProcStatusChanged(self, *, _bClear: bool = True) -> set[int]:
        with self._lockProcData:
            setChanged: set = self._setProcStatusChanged.copy()
            if _bClear is True:
                self._setProcStatusChanged.clear()
            # endif
        # endwith
        return setChanged

    # enddef

    # ##################################################################################################
    def GetProcOutputChanged(self, *, _bClear: bool = True) -> set[int]:
        setChanged: set = self._setProcOutputChanged.copy()
        if _bClear is True:
            self._setProcOutputChanged.clear()
        # endif
        return setChanged

    # enddef

    # ##################################################################################################
    def TerminateAll(self):
        evTerminate: threading.Event = None
        for evTerminate in self._dicProcTerminateEvent.values():
            evTerminate.set()
        # endfor

    # enddef

    # ##################################################################################################
    def TerminateProc(self, _iJobId: int):
        if _iJobId not in self._dicProcTerminateEvent:
            raise RuntimeError("Job Id '{_iJobId}' not available")
        # endif

        self._dicProcTerminateEvent[_iJobId].set()

    # enddef

    # ##################################################################################################
    def UpdateProcOutput(self, *, _iMaxTime_ms: int = 100, _fInitialWaitTime_s: float = 0.0):
        bFirst: bool = True
        iStartTime_ns = time.time_ns()
        while True:
            try:
                if _fInitialWaitTime_s > 0.0 and bFirst is True:
                    iJobId, sLine = self._qProcStdOut.get(timeout=_fInitialWaitTime_s)
                    bFirst = False
                else:
                    iJobId, sLine = self._qProcStdOut.get_nowait()
                # endif
            except queue.Empty:
                break
            # endtry

            xJobOutput: CProcessOutput = self._dicProcOutput.get(iJobId)
            if xJobOutput is not None:
                xJobOutput.AddLine(sLine)
                self._setProcOutputChanged.add(iJobId)
            # endif

            if _iMaxTime_ms > 0 and (time.time_ns() - iStartTime_ns) // 1000000 >= _iMaxTime_ms:
                break
            # endif
        # endwhile

    # enddef

    # ##################################################################################################
    def _CreateCallback_ProcStdOut(self, iId: int):
        def Callback(sLine: str):
            # sys.stdout.write(f"{self._sExecType}, {iIdx}: {sLine}")
            self._qProcStdOut.put((iId, sLine))

        # enddef

        return Callback

    # enddef

    # ##################################################################################################
    def _CreateCallback_ProcStarting(self, iId: int):
        def Callback(lCmd: list[str]):
            with self._lockProcData:
                if iId in self._dicProcStatus:
                    self._dicProcStatus[iId] = EProcessStatus.STARTING
                    self._setProcStatusChanged.add(iId)
                # endif
            # endwith

        # enddef

        return Callback

    # enddef

    # ##################################################################################################
    def _CreateCallback_ProcStarted(self, iId: int):
        def Callback(lCmd: list[str], iPid: int):
            with self._lockProcData:
                if iId in self._dicProcStatus:
                    self._dicProcStatus[iId] = EProcessStatus.RUNNING
                    self._setProcStatusChanged.add(iId)
                # endif
            # endwith

        # enddef

        return Callback

    # enddef

    # ##################################################################################################
    def _CreateCallback_ProcEnded(self, iId: int):
        def Callback(iReturnValue: int, sMsg: str):
            with self._lockProcData:
                if iId in self._dicProcStatus:
                    self._dicProcStatus[iId] = EProcessStatus.ENDED if iReturnValue == 0 else EProcessStatus.TERMINATED
                    self._setProcStatusChanged.add(iId)
                # endif
            # endwith

        # enddef

        return Callback

    # enddef

    # ##################################################################################################
    def _CreateCallback_ProcPollTerminate(self, iId: int):
        def Callback() -> bool:
            return self._dicProcTerminateEvent[iId].is_set()

        # enddef

        return Callback

    # enddef
