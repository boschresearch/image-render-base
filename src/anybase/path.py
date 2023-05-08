#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /path.py
# Created Date: Thursday, October 22nd 2020, 4:26:28 pm
# Author: Christian Perwass
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
from typing import Union
from pathlib import Path
from .cls_any_error import CAnyError, CAnyError_Message

#######################################################################
def ProvideWriteFilepathExt(_xFilepath, _sExt):

    pathFile = MakeNormPath(_xFilepath)
    if len(pathFile.suffix) == 0:
        pathFile = pathFile.parent / (pathFile.name + _sExt)
    # endif

    return pathFile


# enddef


#######################################################################
def ProvideReadFilepathExt(_xFilepath, _lExt, bDoRaise=False):

    pathFile = MakeNormPath(_xFilepath)
    sExt = pathFile.suffix
    if len(sExt) > 0:
        return pathFile
    # endif

    for sExt in _lExt:
        pathNew = pathFile.parent / (pathFile.name + sExt)
        if pathNew.exists():
            return pathNew
        # endif
    # endfor

    if bDoRaise is False:
        return None
    # endif

    if len(pathFile.suffix) == 0:
        sExt = ", ".join(_lExt)
        sFile = "{}[{}]".format(pathFile.name, sExt)
    else:
        sFile = pathFile.name
    # endif
    raise CAnyError_Message(
        sMsg="File '{}' not found at path: {}".format(sFile, pathFile.parent)
    )


# enddef


#######################################################################
def GetRelPathBelow(_sFolderName, _sPath):

    sRelPath = _sPath
    lPath = _sPath.split(os.path.sep)
    iCfgIdx = lPath.index(_sFolderName)
    if iCfgIdx >= 0:
        sRelPath = os.path.sep.join(lPath[iCfgIdx + 1 :])
    # endif

    return sRelPath


# enddef


#######################################################################
def GetParentPathOfFolderInPath(_sLastParent, _sPath):

    lPath = os.path.normpath(_sPath).split(os.path.sep)
    iCfgIdx = lPath.index(_sLastParent)
    if iCfgIdx < 0:
        raise Exception("Cannot find '{0}' folder in script path.".format(_sLastParent))
    # endif

    sMainPath = os.path.sep.join(lPath[0:iCfgIdx])
    return sMainPath


# enddef


#######################################################################
def CreateDir(_xAbsPath):

    if isinstance(_xAbsPath, list):
        sAbsPath = os.path.sep.join(_xAbsPath)
    else:
        sAbsPath = _xAbsPath
    # endif

    if not os.path.exists(sAbsPath):
        try:
            os.makedirs(sAbsPath)
        except Exception:
            pass
        # endtry
    # endif


# enddef


#######################################################################
def NormPath(_xPath: Union[str, Path]):

    if isinstance(_xPath, str):
        return Path(
            os.path.normpath(os.path.expandvars(os.path.expanduser(_xPath)))
        ).as_posix()

    elif isinstance(_xPath, Path):
        return Path(NormPath(_xPath.as_posix()))

    else:
        raise CAnyError_Message(
            sMsg="Path argument has invalid type '{}'".format(
                CAnyError.ToTypename(_xPath)
            )
        )
    # endtry


# enddef


#######################################################################
def MakePath(_xParts: Union[str, list, tuple, Path]) -> Path:

    pathX = None

    if isinstance(_xParts, str):
        pathX = Path(_xParts)

    elif isinstance(_xParts, list) or isinstance(_xParts, tuple):
        if len(_xParts) == 0:
            pathX = Path(".")

        else:
            pathX = MakePath(_xParts[0])
            for xPart in _xParts[1:]:
                pathX /= MakePath(xPart)
            # endfor
        # endif

    elif isinstance(_xParts, Path):
        pathX = _xParts

    else:
        pathX = Path(str(_xParts))

    # endif

    return pathX


# enddef

#######################################################################
def MakeNormPath(_xParts: Union[str, list, tuple, Path]) -> Path:
    return NormPath(MakePath(_xParts))


# enddef
