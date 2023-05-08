#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \filepathvars.py
# Created Date: Tuesday, April 20th 2021, 8:26:16 am
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

# Replace config variables based on a given file path

from pathlib import Path
from . import path


def GetVarDict(_xFilepath):

    xP = path.MakeNormPath(_xFilepath)

    if len(xP.suffix) > 0:
        # assume given filepath is a path to a file
        dicVar = {
            "filebasename": xP.stem,
            "filename": xP.name,
            "fileext": xP.suffix,
            "folder": xP.parent.name,
            "parentfolder": xP.parent.parent.name,
            "path": xP.parent.as_posix(),
            "filepath": xP.as_posix(),
        }
    else:
        # assume given filepath is a path to a folder
        dicVar = {
            "folder": xP.name,
            "parentfolder": xP.parent.name,
            "path": xP.as_posix(),
        }
    # endif

    return dicVar


# enddef
