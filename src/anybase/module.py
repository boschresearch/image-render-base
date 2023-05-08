#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \module.py
# Created Date: Wednesday, January 11th 2023, 2:33:37 pm
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
import inspect
import importlib


########################################################################
def Print(_sText: str, _bDoPrint: bool = True):
    if _bDoPrint is True:
        print(_sText, flush=True)
    # endif


# enddef


########################################################################
def ReloadChildModules(*, _sName: str, _bDoPrint: bool = False):

    lMods = [x for x in sys.modules.keys() if x.startswith(f"{_sName}.")]
    for sMod in lMods:
        try:
            Print(f"Reloading module: {sMod}", _bDoPrint)
            importlib.reload(sys.modules[sMod])

        except Exception as xEx:
            Print(f"Error reloading module '{sMod}':\n{xEx}", _bDoPrint)
        # endtry
    # endfor modules


# enddef


########################################################################
def ReloadModule(*, _sName: str, _bChildren=False, _bDoPrint: bool = False):

    xMod = sys.modules.get(_sName)
    if xMod is not None:
        Print(f"Reloading module '{_sName}'", _bDoPrint)
        try:
            importlib.reload(xMod)
        except Exception as xEx:
            Print(f"Error reloading module '{_sName}':\n{xEx}", _bDoPrint)
        # endtry
    # endif

    if _bChildren is True:
        ReloadChildModules(_sName=_sName, _bDoPrint=_bDoPrint)

    # endif


# enddef


########################################################################
# Reload all child modules of the calling function's module
def ReloadCurrentChildModules(*, _bDoPrint: bool = False):

    xCallFrame = inspect.currentframe().f_back
    if xCallFrame is None:
        return
    # endif

    modCaller = inspect.getmodule(xCallFrame)
    if modCaller is None:
        return
    # endif

    sModName: str = modCaller.__name__

    Print(f"Reloading child modules of '{sModName}'", _bDoPrint)
    ReloadChildModules(_sName=sModName, _bDoPrint=_bDoPrint)


# enddef
