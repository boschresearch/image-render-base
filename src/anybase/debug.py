#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \debug.py
# Created Date: Friday, January 20th 2023, 8:32:15 am
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

import sys
from pathlib import Path
from . import path as anypath

from anybase.cls_any_error import CAnyError_Message
import catharsys.decs.decorator_log as logging_dec


################################################################################################################
def ExtendPathForDebugPy():
    """
    Look for the 'debugpy' module path in the current user's VSCode extensions.
    """

    pathVSCodeExtension: Path = anypath.MakeNormPath(["~", ".vscode", "extensions"])
    if not pathVSCodeExtension.exists():
        raise RuntimeError(f"VSCode extension path does not exist: {(pathVSCodeExtension.as_posix())}")
    # endif

    fLatestTime: float = 0.0
    pathExtDebug: Path = None
    pathExt: Path
    for pathExt in pathVSCodeExtension.iterdir():

        if not pathExt.is_dir():
            continue
        # endif

        if pathExt.name.startswith("ms-python.python") and pathExt.stat().st_mtime > fLatestTime:
            pathExtDebug = pathExt
            fLatestTime = pathExt.stat().st_mtime
        # endif

    # endfor

    if pathExtDebug is None:
        raise RuntimeError("No python extension found in VSCode extensions folder")
    # endif

    lSubPaths: list[str] = ["pythonFiles/lib/python", "python_files/lib/python"]
    for sSubPath in lSubPaths:
        pathExtDebugPython = pathExtDebug / sSubPath
        if pathExtDebugPython.exists():
            break
        # endif
        pathExtDebugPython = None
    # endfor

    if pathExtDebugPython is None:
        lPaths: list[str] = [(pathExtDebug / sSubPath).as_posix() for sSubPath in lSubPaths]
        sPaths = "\n".join(lPaths)
        raise RuntimeError(f"VSCode python extension has no python files at either of the paths:\n{sPaths}")
    # endif

    logging_dec.logFunctionCall.PrintLog(f"Using 'debugpy' module at path: {(pathExtDebugPython.as_posix())}")

    sPathDebugPy = pathExtDebugPython.as_posix()
    if sPathDebugPy not in sys.path:
        sys.path.append(sPathDebugPy)
    # endif


# enddef


################################################################################################################
def ImportDebugPy():

    ExtendPathForDebugPy()
    try:
        import debugpy
    except Exception as xEx:
        raise CAnyError_Message(sMsg="Cannot import 'debugpy' despite setting VSCode debugpy path", xChildEx=xEx)
    # endtry

    return debugpy


# enddef

################################################################################################################
def WaitForClient(_iDebugPort: int):

    debugpy = ImportDebugPy()

    debugpy.listen(_iDebugPort)

    print("Waiting for debugger attach")

    debugpy.wait_for_client()
    debugpy.breakpoint()
    print("Debugger attached successfully.")


# enddef


################################################################################################################
def CreateHandler_CheckDebugPortOpen(*, _fTimeoutSeconds: float, _sIp: str, _iPort: int):

    from anybase import net

    # The handler function, receives the command and the arguments with which
    # Process was started in 'lCmd'.
    # The iPid contains the process id returned by subprocess.Popen.
    # Unfortunately, at least in the case of Blender, this pid does not relate to the process that actually starts
    # the debugpy debugger and opens the port. Therefore, we need to look for any
    # process that opens the debug port on the local host.
    def Handler(lCmd: list, iPid: int):

        print(f"Starting Catharsys debugging on port {_iPort}...", flush=True)

        if net.IsPortOpen(_sIp, _iPort, _fTimeoutSeconds=_fTimeoutSeconds, _bDoPrint=True) is True:
            print(f"Catharsys debug port open at '{_sIp}:{_iPort}'", flush=True)
        else:
            print(
                f"ERROR: Catharsys debug port {_iPort} NOT open at {_sIp} after waiting {_fTimeoutSeconds} seconds",
                flush=True,
            )
        # endif

    # enddef
    return Handler


# enddef
