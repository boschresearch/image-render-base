#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \link.py
# Created Date: Friday, October 1st 2021, 1:05:00 pm
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
import platform
import subprocess
from pathlib import Path

######################################################################
def islink(_sPath):

    if platform.system() == "Windows":
        procChild = subprocess.Popen(
            'fsutil reparsepoint query "{}"'.format(_sPath), stdout=subprocess.PIPE
        )

        streamData = procChild.communicate()[0]
        iReturnCode = procChild.returncode
        # print("IsLink: {}, {}".format(_sPath, iReturnCode))
        return iReturnCode == 0

    else:
        return os.path.islink(_sPath)
    # endif


# enddef


######################################################################
def symlink(_sSrc, _sDst):

    if platform.system() == "Windows":
        sSrc = _sSrc.replace("/", "\\")
        sDst = _sDst.replace("/", "\\")

        procChild = subprocess.Popen(
            ["MKLINK", "/J", sDst, sSrc],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        streamData = procChild.communicate()[0]
        iReturnCode = procChild.returncode
        # print("SymLink: {}, {}, {}".format(_sSrc, _sDst, iReturnCode))
        if iReturnCode != 0:
            raise RuntimeError(
                "Error creating junction: {} => {}:\n{}\n".format(
                    sDst, sSrc, streamData.decode("utf-8")
                )
            )
        # endif

    else:
        os.symlink(_sSrc, _sDst)

    # endif


# enddef


######################################################################
def unlink(_sPath):

    if not islink(_sPath):
        raise RuntimeError("Path is not a link: {}".format(_sPath))
    # endif

    if platform.system() == "Windows":
        os.rmdir(_sPath)

    else:
        os.unlink(_sPath)

    # endif


# enddef
