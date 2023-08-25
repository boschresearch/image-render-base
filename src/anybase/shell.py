#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \shell.py
# Created Date: Friday, May 6th 2022, 10:13:25 am
# Author: Christian Perwass (CR/AEC5)
# <LICENSE id="Apache-2.0">
#
#   Image-Render Base Functions module
#   Copyright 2022 Robert Bosch GmbH and its subsidiaries
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


import os
import time
import queue
import threading
import select
from typing import Callable, Optional, Union, IO

# import asyncio
import subprocess
import tempfile
from pathlib import Path
from .cls_any_error import CAnyError_Message
from .cls_process_handler import CProcessHandler


#################################################################################################################
def ExecCmd(
    *,
    sCmd: str,
    sCwd: Optional[str] = None,
    bDoPrint: bool = False,
    bDoPrintOnError: bool = False,
    bDoRaiseOnError: bool = False,
    bReturnStdOut: bool = False,
    sPrintPrefix: str = "",
    dicEnv: Optional[dict] = None,
    xProcHandler: Optional[CProcessHandler] = None,
) -> Union[tuple[bool, list[str]], bool]:
    if sCwd is None:
        sEffCwd = os.getcwd()
    else:
        sEffCwd = sCwd
    # endif

    dicEnviron = os.environ.copy()
    if dicEnv is not None:
        dicEnviron.update(dicEnv)
    # endif

    return _ExecProc(
        xCmd=sCmd,
        sCwd=sEffCwd,
        dicEnviron=dicEnviron,
        bShell=True,
        bDoPrint=bDoPrint,
        bDoPrintOnError=bDoPrintOnError,
        bDoRaiseOnError=bDoRaiseOnError,
        bReturnStdOut=bReturnStdOut,
        sPrintPrefix=sPrintPrefix,
        xProcHandler=xProcHandler,
    )


# enddef


#################################################################################################################
def ExecShellCmds(
    *,
    sShellPath: str,
    lCmds: list[str],
    sCwd: Optional[str] = None,
    bDoPrint: bool = False,
    bDoPrintOnError: bool = False,
    bDoRaiseOnError: bool = False,
    bReturnStdOut: bool = False,
    sPrintPrefix: str = "",
    dicEnv: Optional[dict] = None,
    xProcHandler: Optional[CProcessHandler] = None,
) -> Union[tuple[bool, list[str]], bool]:
    if not isinstance(lCmds, list):
        raise CAnyError_Message(sMsg="Argument 'lCmds' must be a list")
    # endif

    if sCwd is None:
        sEffCwd = os.getcwd()
    else:
        sEffCwd = sCwd
    # endif

    dicEnviron = os.environ.copy()
    if dicEnv is not None:
        dicEnviron.update(dicEnv)
    # endif

    sCmd = "\n".join(lCmds)

    pathScript = None
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ps1") as xFile:
        pathScript = Path(xFile.name)
        xFile.write(sCmd)
    # endwith

    lCmd = [sShellPath, pathScript.as_posix()]

    return _ExecProc(
        xCmd=lCmd,
        sCwd=sEffCwd,
        dicEnviron=dicEnviron,
        bShell=False,
        bDoPrint=bDoPrint,
        bDoPrintOnError=bDoPrintOnError,
        bDoRaiseOnError=bDoRaiseOnError,
        bReturnStdOut=bReturnStdOut,
        sPrintPrefix=sPrintPrefix,
        xProcHandler=xProcHandler,
    )


# enddef


#################################################################################################################
def ExecPowerShellCmds(
    *,
    lCmds: list[str],
    sCwd: Optional[str] = None,
    bDoPrint: bool = False,
    bDoPrintOnError: bool = False,
    bDoRaiseOnError: bool = False,
    bReturnStdOut: bool = False,
    sPrintPrefix: str = "",
    dicEnv: Optional[dict] = None,
    xProcHandler: Optional[CProcessHandler] = None,
) -> Union[tuple[bool, list[str]], bool]:
    return ExecShellCmds(
        sShellPath="powershell.exe",
        lCmds=lCmds,
        sCwd=sCwd,
        bDoPrint=bDoPrint,
        bDoPrintOnError=bDoPrintOnError,
        bDoRaiseOnError=bDoRaiseOnError,
        bReturnStdOut=bReturnStdOut,
        sPrintPrefix=sPrintPrefix,
        dicEnv=dicEnv,
        xProcHandler=xProcHandler,
    )


# enddef


#################################################################################################################
def ExecBashCmds(
    *,
    lCmds: list[str],
    sCwd: Optional[str] = None,
    bDoPrint: bool = False,
    bDoPrintOnError: bool = False,
    bDoRaiseOnError: bool = False,
    bReturnStdOut: bool = False,
    sPrintPrefix: str = "",
    dicEnv: Optional[dict] = None,
    xProcHandler: Optional[CProcessHandler] = None,
) -> Union[tuple[bool, list[str]], bool]:
    return ExecShellCmds(
        sShellPath="/bin/bash",
        lCmds=lCmds,
        sCwd=sCwd,
        bDoPrint=bDoPrint,
        bDoPrintOnError=bDoPrintOnError,
        bDoRaiseOnError=bDoRaiseOnError,
        bReturnStdOut=bReturnStdOut,
        sPrintPrefix=sPrintPrefix,
        dicEnv=dicEnv,
        xProcHandler=xProcHandler,
    )


# enddef


#################################################################################################################
def ExecProgram(
    *,
    sProgram: str,
    lArgs: list[str] = [],
    sCwd: Optional[str] = None,
    bDoPrint: bool = False,
    bDoPrintOnError: bool = False,
    bDoRaiseOnError: bool = False,
    bReturnStdOut: bool = False,
    sPrintPrefix: str = "",
    dicEnv: Optional[dict] = None,
    xProcHandler: Optional[CProcessHandler] = None,
) -> Union[tuple[bool, list[str]], bool]:
    if sCwd is None:
        sEffCwd = os.getcwd()
    else:
        sEffCwd = sCwd
    # endif

    dicEnviron = os.environ.copy()
    if dicEnv is not None:
        dicEnviron.update(dicEnv)
    # endif

    lCmd = [sProgram]
    lCmd.extend(lArgs)

    return _ExecProc(
        xCmd=lCmd,
        sCwd=sEffCwd,
        dicEnviron=dicEnviron,
        bShell=False,
        bDoPrint=bDoPrint,
        bDoPrintOnError=bDoPrintOnError,
        bDoRaiseOnError=bDoRaiseOnError,
        bReturnStdOut=bReturnStdOut,
        sPrintPrefix=sPrintPrefix,
        xProcHandler=xProcHandler,
    )


# enddef


#################################################################################################################
def _ReadPipeToQueue(_xPipe: IO[str], _qLines: queue.Queue):
    for sLine in iter(_xPipe.readline, ""):
        _qLines.put(sLine)
    # endfor
    _xPipe.close()

    # # print(">> READ PIPE TO QUEUE ENDED")


# enddef


#################################################################################################################
def _ExecProc(
    *,
    xCmd: Union[str, list],
    sCwd: str,
    dicEnviron: dict,
    bShell: bool,
    bDoPrint: bool = False,
    bDoPrintOnError: bool = False,
    bDoRaiseOnError: bool = False,
    bReturnStdOut: bool = False,
    sPrintPrefix: str = "",
    xProcHandler: Optional[CProcessHandler] = None,
) -> Union[tuple[bool, list[str]], bool]:
    lCmd: list = None
    if isinstance(xCmd, list):
        lCmd = xCmd
    else:
        lCmd = [xCmd]
    # endif

    if xProcHandler is None:
        xProcHandler = CProcessHandler()
    # endif

    if xProcHandler.bPollTerminateAvailable and xProcHandler.PollTerminate() is True:
        if bReturnStdOut is True:
            return False, []
        else:
            return False
        # endif
    # endif

    if xProcHandler.bPreStartAvailable:
        xProcHandler.PreStart(lCmd)
    # endif

    qLines = queue.Queue()

    procChild = subprocess.Popen(
        xCmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=bShell,
        cwd=sCwd,
        universal_newlines=True,
        env=dicEnviron,
    )

    threadRead = threading.Thread(target=_ReadPipeToQueue, args=(procChild.stdout, qLines), daemon=True)
    threadRead.start()

    if xProcHandler.bPostStartAvailable:
        xProcHandler.PostStart(lCmd, procChild.pid)
    # endif

    lLines = []
    bTerminate: bool = False

    while True:
        while True:
            if xProcHandler.bPollTerminateAvailable:
                bTerminate = xProcHandler.PollTerminate()
                if bTerminate is True:
                    break
                # endif
            # endif

            try:
                sLine = qLines.get_nowait()
            except queue.Empty:
                break
            # endtry

            if xProcHandler.bStdOutAvailable:
                xProcHandler.StdOut(sLine)
            else:
                lLines.append(sLine)
                if bDoPrint:
                    print(sPrintPrefix + sLine, end="", flush=True)
                # endif
            # endif

        # endwhile read lines from queue

        if bTerminate is True:
            break
        # endif

        try:
            procChild.wait(timeout=0.01)
            # print(f">> PROCESS ENDED: {lCmd}")
            break
        except subprocess.TimeoutExpired:
            pass
        # endtry

        # See whether read thread has ended
        threadRead.join(0.1)
        if threadRead.is_alive() is False:
            # print(f">> Read Thread Ended: {lCmd}")
            break
        # endif
    # endwhile waiting for process output

    # Read remaining lines
    while True:
        try:
            sLine = qLines.get_nowait()
        except queue.Empty:
            break
        # endtry

        if xProcHandler.bStdOutAvailable:
            xProcHandler.StdOut(sLine)
        else:
            lLines.append(sLine)
            if bDoPrint:
                print(sPrintPrefix + sLine, end="", flush=True)
            # endif
        # endif

    # endwhile read lines from queue

    if bTerminate is True:
        procChild.terminate()
    # endif

    # procChild.stdout.close()
    iReturnCode = procChild.wait()

    # if threadRead.is_alive() is True:
    #     print(f">>! Read Thread still alive: {lCmd}")
    # # endif

    if iReturnCode != 0:
        if bDoRaiseOnError:
            if xProcHandler.bEndedAvailable:
                xProcHandler.Ended(iReturnCode, "")
            # endif
            raise subprocess.CalledProcessError(iReturnCode, lCmd)

        elif (not bDoPrint and bDoPrintOnError is True) or xProcHandler.bEndedAvailable:
            sMsg = sPrintPrefix + "ERROR:\n"
            for sLine in lLines:
                sMsg += sPrintPrefix + "! " + sLine
            # endfor

            if xProcHandler.bEndedAvailable:
                xProcHandler.Ended(iReturnCode, sMsg)
            else:
                print(sMsg)
            # endif
        # endif
    elif xProcHandler.bEndedAvailable:
        xProcHandler.Ended(iReturnCode, "")
    # endif

    if bReturnStdOut is True:
        return iReturnCode == 0, lLines
    else:
        return iReturnCode == 0
    # endif


# enddef
