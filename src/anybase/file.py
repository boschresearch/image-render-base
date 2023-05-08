#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /file.py
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
import sys
import re
import pyjson5
import json
from pathlib import Path
from anybase.cls_any_error import CAnyError, CAnyError_Message
from anybase.path import MakeNormPath


#######################################################################
# Load JSON file from path
def LoadJson(_xFilePath) -> dict:

    pathFile = MakeNormPath(_xFilePath)

    try:
        with pathFile.open("r") as xFile:
            dicData = pyjson5.decode_io(xFile)
        # endwith
    except pyjson5.Json5IllegalCharacter as xEx:
        print(xEx.message)
        xMatch = re.search(r"near\s+(\d+),", xEx.message)
        if xMatch is None:
            raise CAnyError_Message(
                sMsg=CAnyError.ListToString(
                    [
                        "Illegal character encountered while parsing JSON file",
                        xEx.message,
                        pathFile.as_posix(),
                    ]
                )
            )
        # endif
        iCharPos = int(xMatch.group(1))
        sText = pathFile.read_text()
        lLines = sText.split("\n")
        iCharCnt = 0
        iLinePos = len(lLines) - 1

        for iLineIdx, sLine in enumerate(lLines):
            iCharCnt += len(sLine) + 1
            if iCharCnt >= iCharPos:
                iLinePos = iLineIdx
                break
            # endif
        # endfor

        # From character position, subtract length of line with error and
        # the numer of lines before this line, to subtract the newline characters
        iCharPosInLine = min(
            len(lLines[iLinePos]) - 1,
            max(0, iCharPos - (iCharCnt - len(lLines[iLinePos]))),
        )

        lMsg = [
            "Unexpected character '{}' encountered in line {} at position {}".format(
                xEx.character, iLinePos + 1, iCharPosInLine + 1
            )
        ]
        iLineStart = max(0, iLinePos - 1)
        iLineEnd = min(len(lLines) - 1, iLinePos + 1)
        for iLineIdx in range(iLineStart, iLineEnd + 1):
            sLine = lLines[iLineIdx]
            if iLineIdx == iLinePos:
                sMsg = ">{:3d}<: ".format(iLineIdx + 1)
                sMsg += sLine[0:iCharPosInLine]
                sMsg += ">{}<".format(sLine[iCharPosInLine])
                sMsg += sLine[iCharPosInLine + 1 :]
            else:
                sMsg = " {:3d} :  {}".format(iLineIdx + 1, sLine)
            # endif
            lMsg.append(sMsg)
        # endfor
        raise CAnyError_Message(
            sMsg="Error parsing JSON file: {}{}".format(
                pathFile.as_posix(), CAnyError.ListToString(lMsg)
            )
        )
    # endtry

    return dicData


# enddef


#######################################################################
# save JSON file from relative path to script path
def SaveJson(_xFilePath, _dicData, iIndent=-1):

    pathFile = MakeNormPath(_xFilePath)

    with pathFile.open("w") as xFile:
        if iIndent < 0 or pathFile.suffix == ".json5" or pathFile.suffix == ".ison":
            pyjson5.encode_io(_dicData, xFile, supply_bytes=False)
        else:
            json.dump(_dicData, xFile, indent=iIndent)
        # endif
    # endwith


# enddef


#######################################################################
# Save Python object as Pickle file
def SavePickle(_xFilePath, _dicData):
    import pickle

    pathFile = MakeNormPath(_xFilePath)

    with pathFile.open("wb") as xFile:
        pickle.dump(_dicData, xFile)
    # endwith


# enddef

#######################################################################
# Load Pickel file from path
def LoadPickle(_xFilePath):
    import pickle

    pathFile = MakeNormPath(_xFilePath)

    dicData = None
    with pathFile.open("rb") as xFile:
        dicData = pickle.load(xFile)
    # endwith

    return dicData


# enddef

#######################################################################
# Save text file from relative path to script path
def LoadText(_xFilePath):

    pathFile = MakeNormPath(_xFilePath)

    sText = ""
    with pathFile.open("r") as xFile:
        sText = xFile.read()
    # endwith

    return sText


# enddef

#######################################################################
# Save text file from relative path to script path
def SaveText(_xFilePath, _sText):

    pathFile = MakeNormPath(_xFilePath)
    with pathFile.open("w") as xFile:
        xFile.write(_sText)
    # endwith


# enddef
