#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \plugin.py
# Created Date: Thursday, May 12th 2022, 11:37:58 am
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

from importlib import metadata

from catharsys.util import config
from anybase.cls_any_error import CAnyError, CAnyError_Message, CAnyError_TaskMessage


##################################################################################################
def SelectEntryPointFromDti(*, sGroup, sTrgDti, sTypeDesc):

    try:
        lGrpDti = []
        # print(f"Group: {sGroup}")
        clnEpGrp = metadata.entry_points().select(group=sGroup)
        if len(clnEpGrp) == 0:
            raise CAnyError_Message(sMsg=f"No {sTypeDesc} available")
        # endif

        epTrg = None
        for epTrgTest in clnEpGrp:
            # print("Found: {}".format(epTrgTest.name))
            if epTrgTest.name in lGrpDti:
                continue
            # endif
            lGrpDti.append(epTrgTest.name)
            dicRes = config.CheckDti(epTrgTest.name, sTrgDti)
            if dicRes["bOK"] is True:
                # print("...selected")
                epTrg = epTrgTest
                break
            # endif
        # endfor

        if epTrg is None:
            raise CAnyError_Message(
                sMsg="No matching {} found for id '{}'\n"
                "Available types are:\n{}".format(sTypeDesc, sTrgDti, CAnyError.ListToString(lGrpDti))
            )
        # endif

    except Exception as xEx:
        raise CAnyError_TaskMessage(
            sTask=f"Selection of {sTypeDesc}",
            sMsg=f"DTI not available: {sTrgDti}",
            xChildEx=xEx,
        )
    # endtry

    return epTrg


# enddef
