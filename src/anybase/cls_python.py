#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_python.py
# Created Date: Tuesday, May 24th 2022, 3:46:32 pm
# Author: Christian Perwass (CR/AEC5)
# <LICENSE id="Apache-2.0">
#
#   Image-Render Standard Actions module
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
import platform
from pathlib import Path
from typing import Callable, Optional

from . import shell
from . import path as cathpath
from .cls_any_error import CAnyError_Message


#####################################################################
class CPythonConfig:
    @property
    def sSystem(self):
        return self._sSystem

    # enddef

    @property
    def bIsWindows(self):
        return self._sSystem == "Windows"

    # enddef

    @property
    def bIsLinux(self):
        return self._sSystem == "Linux"

    # enddef

    @property
    def sPathPython(self):
        if self._pathPython is not None:
            return self._pathPython.as_posix()
        else:
            return None
        # endif

    # enddef

    @property
    def sCondaEnv(self):
        return self._sCondaEnv

    # enddef

    @property
    def sPythonProg(self):
        if self.bIsWindows:
            return "python.exe"
        elif self.bIsLinux:
            return "python"
        # endif
        return None

    # enddef

    #####################################################################
    def __init__(self, *, xPythonPath=None, sCondaEnv=None):
        self._pathPython: Path = None
        self._sCondaEnv: str = None
        self._sSystem: str = None

        if xPythonPath is not None:
            self._pathPython = cathpath.MakeNormPath(xPythonPath)
        # endif

        if isinstance(sCondaEnv, str):
            self._sCondaEnv = sCondaEnv
        # endif

        self._sSystem = platform.system()
        if self._sSystem not in ["Windows", "Linux"]:
            raise CAnyError_Message(sMsg="Unsupported platform '{}'".format(self.sSystem))
        # endif

    # enddef

    #####################################################################
    def _GetCondaActCmd(self):
        lCmd = []
        if self.bIsWindows:
            pathHook = Path(os.path.expanduser("~/Anaconda3/shell/condabin/conda-hook.ps1"))
            # pathHook = Path("{}/Anaconda3/shell/condabin/conda-hook.ps1".format(os.environ.get("HOME")))
            if not pathHook.exists():
                pathHook = Path("{}/Anaconda3/shell/condabin/conda-hook.ps1".format(os.environ.get("PROGRAMFILES")))
                if not pathHook.exists():
                    raise CAnyError_Message(sMsg="Cannot find conda activation script 'conda-hook.ps1'")
                # endif
            # endif
            lCmd.extend(
                [
                    "invoke-expression -Command \"& '{}'\"".format(pathHook.as_posix()),
                    "conda activate {}".format(self._sCondaEnv),
                ]
            )

        elif self.bIsLinux:
            lCmd.extend(["source ~/.bashrc", "conda activate {}".format(self._sCondaEnv)])

        else:
            raise CAnyError_Message(sMsg="Unsupported platform '{}'".format(self.sSystem))
        # endif

        return lCmd

    # enddef

    #####################################################################
    def ExecPython(
        self,
        *,
        lArgs,
        xCwd=None,
        bDoPrint=False,
        bDoPrintOnError=False,
        bDoRaiseOnError=False,
        bReturnStdOut=False,
        sPrintPrefix="",
        dicEnv=None,
        funcPreStart: Optional[Callable[[list], None]] = None,
        funcPostStart: Optional[Callable[[list, int], None]] = None,
    ):
        lCmds = []
        sCwd = None

        if isinstance(self._sCondaEnv, str):
            lCmds.extend(self._GetCondaActCmd())
        # endif

        if isinstance(self._pathPython, Path):
            if not self._pathPython.exists():
                raise CAnyError_Message(sMsg="Python path not found: {}".format(self._pathPython.as_posix()))
            # endif
            pathPyCmd = self._pathPython / self.sPythonProg
            if not pathPyCmd.exists():
                raise CAnyError_Message(sMsg="Python does not exist at path: {}".format(pathPyCmd.as_posix()))
            # endif
            sPyCmd = pathPyCmd.as_posix()

        else:
            sPyCmd = self.sPythonProg
        # endif

        if len(lArgs) > 0:
            sPyCmd += " " + " ".join(lArgs)
        # endif
        lCmds.append(sPyCmd)

        if xCwd is not None:
            sCwd = cathpath.MakeNormPath(xCwd)
        # endif

        iReturnCode = None
        if self.bIsWindows:
            iReturnCode = shell.ExecPowerShellCmds(
                lCmds=lCmds,
                sCwd=sCwd,
                bDoPrint=bDoPrint,
                bDoPrintOnError=bDoPrintOnError,
                bDoRaiseOnError=bDoRaiseOnError,
                bReturnStdOut=bReturnStdOut,
                sPrintPrefix=sPrintPrefix,
                dicEnv=dicEnv,
                funcPreStart=funcPreStart,
                funcPostStart=funcPostStart,
            )
        elif self.bIsLinux:
            iReturnCode = shell.ExecBashCmds(
                lCmds=lCmds,
                sCwd=sCwd,
                bDoPrint=bDoPrint,
                bDoPrintOnError=bDoPrintOnError,
                bDoRaiseOnError=bDoRaiseOnError,
                bReturnStdOut=bReturnStdOut,
                sPrintPrefix=sPrintPrefix,
                dicEnv=dicEnv,
                funcPreStart=funcPreStart,
                funcPostStart=funcPostStart,
            )
        # endif

        return iReturnCode

    # enddef


# endclass
