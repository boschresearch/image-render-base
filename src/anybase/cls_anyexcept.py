#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_anyexcept.py
# Created Date: Friday, March 19th 2021, 9:03:02 am
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


class CAnyExcept(Exception):
    def __init__(self, _sMsg, xEx=None):

        if xEx is not None:
            lMsg = [_sMsg]
            lLines = str(xEx).split("\n")
            for sLine in lLines:
                if sLine.startswith(">"):
                    sLine = ">" + sLine
                else:
                    sLine = "> " + sLine
                # endif
                lMsg.append(sLine)
            # endfor

            self.message = "\n".join(lMsg)
        else:
            self.message = _sMsg
        # endif
        super().__init__(self.message)

    # enddef

    ##################################################################################
    @staticmethod
    def Print(_xEx, bTraceback=False):

        import traceback

        print("")
        print("===================================================================")
        print("EXCEPTION ({0})".format(type(_xEx)))
        print(_xEx)
        print("")
        if bTraceback:
            traceback.print_exception(type(_xEx), _xEx, _xEx.__traceback__)
        # endif
        print("===================================================================")
        print("")

    # enddef


# endclass
