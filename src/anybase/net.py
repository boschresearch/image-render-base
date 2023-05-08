#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \net.py
# Created Date: Friday, January 20th 2023, 8:39:57 am
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
import math
import time
import psutil


################################################################################################################
def IsPortOpen(_sIp: str, _iPort: int, *, _fTimeoutSeconds: float = 10.0, _bDoPrint: bool = True) -> bool:

    bIsOpen = False
    iCnt = math.ceil(_fTimeoutSeconds)
    for iIdx in range(iCnt):
        if _bDoPrint is True:
            sys.stdout.write(f"Looking for debug socket '{_sIp}:{_iPort}'... ({iIdx}s of {_fTimeoutSeconds}s)\r")
            sys.stdout.flush()
        # endif

        lConnect = psutil.net_connections()
        xC = next((x for x in lConnect if x.laddr.ip == _sIp and x.laddr.port == _iPort), None)
        if xC is not None:
            bIsOpen = True
            # print(xC)
            break
        # endif
        time.sleep(1.0)
    # endfor
    if _bDoPrint is True:
        sys.stdout.write("                                                                          \r")
        sys.stdout.flush()
    # endif

    return bIsOpen


# enddef
