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

from typing import Callable, Optional

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
):
    if sCwd is None:
        sEffCwd = os.getcwd()
    else:
        sEffCwd = sCwd
    # endif

    dicEnviron = os.environ.copy()
    if dicEnv is not None:
        dicEnviron.update(dicEnv)
    # endif

    if xProcHandler.bPreStartAvailable:
        xProcHandler.PreStart([sCmd])
    # endif

    procChild = subprocess.Popen(
        sCmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=sEffCwd,
        universal_newlines=True,
        env=dicEnviron,
    )

    if xProcHandler.bPostStartAvailable:
        xProcHandler.PostStart([sCmd], procChild.pid)
    # endif

    lLines = []

    if xProcHandler.bStdOutAvailable:
        for sLine in iter(procChild.stdout.readline, ""):
            xProcHandler.StdOut(sLine)
        # endfor
    else:
        for sLine in iter(procChild.stdout.readline, ""):
            lLines.append(sLine)
            if bDoPrint:
                print(sPrintPrefix + sLine, end="", flush=True)
            # endif
        # endfor
    # endif

    procChild.stdout.close()
    iReturnCode = procChild.wait()

    if iReturnCode != 0:
        if bDoRaiseOnError:
            if xProcHandler.bEndedAvailable:
                xProcHandler.Ended(iReturnCode, "")
            # endif
            raise subprocess.CalledProcessError(iReturnCode, sCmd)

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
):
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

    if xProcHandler.bPreStartAvailable:
        xProcHandler.PreStart(lCmd)
    # endif

    procChild = subprocess.Popen(
        lCmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
        cwd=sEffCwd,
        universal_newlines=True,
        env=dicEnviron,
    )

    if xProcHandler.bPostStartAvailable:
        xProcHandler.PostStart(lCmd, procChild.pid)
    # endif

    lLines = []

    if xProcHandler.bStdOutAvailable:
        for sLine in iter(procChild.stdout.readline, ""):
            xProcHandler.StdOut(sLine)
        # endfor
    else:
        for sLine in iter(procChild.stdout.readline, ""):
            lLines.append(sLine)
            if bDoPrint:
                print(sPrintPrefix + sLine, end="", flush=True)
            # endif
        # endfor
    # endif

    procChild.stdout.close()
    iReturnCode = procChild.wait()
    pathScript.unlink()

    if iReturnCode != 0:
        if bDoRaiseOnError:
            if xProcHandler.bEndedAvailable:
                xProcHandler.Ended(iReturnCode, "")
            # endif
            raise subprocess.CalledProcessError(iReturnCode, sCmd)

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
):
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
):
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
async def ReadPipe(pipeX):
    while True:
        print("Read pipe")
        sText = await pipeX.read(10)
        if not sText:
            break
        else:
            print(sText)
        # endif
    # endwhile


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
):
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

    # async def DoExec():
    #     print(f"Starting program '{sProgram}' with args: {lArgs}")
    #     procX = await asyncio.create_subprocess_exec(
    #         sProgram, *lArgs, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    #     )

    #     await asyncio.gather(ReadPipe(procX.stdout), ReadPipe(procX.stderr))

    # # enddef

    # print("Starting async...")
    # asyncio.run(DoExec())
    # return True

    if xProcHandler.bPreStartAvailable:
        xProcHandler.PreStart(lCmd)
    # endif

    procChild = subprocess.Popen(
        lCmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
        cwd=sEffCwd,
        universal_newlines=True,
        env=dicEnviron,
    )

    if xProcHandler.bPostStartAvailable:
        xProcHandler.PostStart(lCmd, procChild.pid)
    # endif

    lLines = []

    if xProcHandler.bStdOutAvailable:
        for sLine in iter(procChild.stdout.readline, ""):
            xProcHandler.StdOut(sLine)
        # endfor
    else:
        for sLine in iter(procChild.stdout.readline, ""):
            lLines.append(sLine)
            if bDoPrint:
                print(sPrintPrefix + sLine, end="", flush=True)
            # endif
        # endfor
    # endif

    procChild.stdout.close()
    iReturnCode = procChild.wait()

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
