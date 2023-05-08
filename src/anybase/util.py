#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \util.py
# Created Date: Friday, May 20th 2022, 10:53:57 am
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


########################################################################
# Recursively update target dictionary with source dictionary
def DictRecursiveUpdate(_dicTrg, _dicSrc):

    if not isinstance(_dicTrg, dict) or not isinstance(_dicSrc, dict):
        raise RuntimeError("Invalid arguments: expect dictionaries")
    # endif

    for sSrcKey in _dicSrc:
        if (
            sSrcKey in _dicTrg
            and isinstance(_dicTrg[sSrcKey], dict)
            and isinstance(_dicSrc[sSrcKey], dict)
        ):
            DictRecursiveUpdate(_dicTrg[sSrcKey], _dicSrc[sSrcKey])
        else:
            _dicTrg[sSrcKey] = _dicSrc[sSrcKey]
        # endif
    # endfor


# enddef
