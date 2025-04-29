#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cml\cls_parser_exception.py
# Created Date: Sunday, February 13th 2022, 11:46:03 am
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

from anybase.logging import logger as clog

################################################################################
def _print(_sText: str):
    print(_sText, flush=True)


# enddef


################################################################################
class CAnyError(RuntimeError):
    def __init__(self, *, sMsg, sType=None, xData=None, xSelect=None, xChildEx=None):

        self.sType = sType
        self.xData = xData
        self.xSelect = xSelect
        self.xChildEx = xChildEx

        import traceback  # lazy import, only necessary for error case
        from . import assertion

        if assertion.IsEnabled() is True:  # (assertion/debugging) is enabled (implicitly set by --debug cmd line option)
            lsStack = traceback.format_stack()
            for sStack in reversed(lsStack):
                if "cls_any_error" not in sStack:
                    self.message = sMsg + "\n" + sStack
                    break
                # endif
            # endfor

            # more explanation on Errors
            if xChildEx is not None and not isinstance(xChildEx, CAnyError):
                self.message += f"\nbuilt-in error {type(xChildEx)}"
                if isinstance(xChildEx, SyntaxError):
                    self.message += f" at ({xChildEx.lineno}): '{xChildEx.filename}'"
                else:
                    self.message += f" '{str(xChildEx)}'"

                    xTrace = xChildEx.__traceback__
                    xTraceNext = xTrace.tb_next if xTrace is not None else None
                    while xTraceNext:
                        xTrace = xTraceNext
                        xTraceNext = xTrace.tb_next if xTrace is not None else None
                    # end while

                    if xTrace is not None:
                        sFrame = str(xTrace.tb_frame)
                        sFrame = sFrame.replace(", file", "\n             file")
                        sFrame = sFrame.replace(", code", "\n             code")
                        self.message += f"\nmost recent: {sFrame}"
                    # endif
                # endif
            # endif

        else:  # only error messages
            self.message = sMsg
        # endif debug

        super().__init__(self.message)

    # enddef

    ################################################################################
    def ToString(self, iLevel=1):

        sMsg = self.IndentLevel(self.message, iLevel)

        if self.xChildEx is not None:
            if isinstance(self.xChildEx, CAnyError) is True:
                sMsg += self.xChildEx.ToString(iLevel=iLevel + 1)
            else:
                sMsg += self.IndentLevel(str(self.xChildEx), iLevel + 1)
            # endif
        # endif

        return sMsg

    # enddef

    ################################################################################
    def IndentLevel(self, _sMsg, _iLevel):

        lLines = _sMsg.split("\n")
        sTag1 = f"{_iLevel:2d}> "
        sTagX = "  | "
        sMsg = sTag1 + lLines[0] + "\n"

        for sLine in lLines[1:]:
            sMsg += sTagX + sLine + "\n"
        # endfor

        return sMsg

    # enddef

    ################################################################################
    @staticmethod
    def ListToString(_lArgs, iHighlightIdx=None):

        sMsg = ""
        if _lArgs is None:
            sMsg += "\nNone"
        elif len(_lArgs) == 0:
            sMsg += "\n[]"
        else:
            for iIdx, xArg in enumerate(_lArgs):
                if iHighlightIdx is not None and iHighlightIdx == iIdx:
                    sMsg += "\n>"
                else:
                    sMsg += "\n "
                # endif
                sMsg += "{:2d}: {}".format(iIdx + 1, str(xArg))
            # endfor
        # endif
        return sMsg

    # enddef

    ################################################################################
    @staticmethod
    def ToTypename(xValue):

        if xValue is None:
            return "None"
        # endif

        sType = "unknown"
        if isinstance(xValue, dict):
            sType = "dictionary"

        elif isinstance(xValue, list):
            sType = "list"

        elif isinstance(xValue, tuple):
            sType = "tuple"

        elif isinstance(xValue, str):
            sType = "string"

        elif isinstance(xValue, int):
            sType = "integer"

        elif isinstance(xValue, float):
            sType = "float"

        elif isinstance(xValue, bool):
            sType = "boolean"

        else:
            sType = str(type(xValue))
        # endif

        return sType

    # enddef

    ################################################################################
    @staticmethod
    def Print(_xEx, sMsg=None, bTraceback=False):

        if isinstance(_xEx, CAnyError):
            sText = _xEx.ToString()
        else:
            sText = str(_xEx)
        # endif

        import traceback

        _print("")
        _print("===================================================================")
        if sMsg is not None:
            # clog.error(sMsg)
            print(sMsg)
        else:
            # clog.error("ERROR")
            print("ERROR")
        # endif
        # clog.error(sText)
        print(sText)
        if bTraceback:
            lEx = traceback.format_exception(type(_xEx), _xEx, _xEx.__traceback__)
            for sLine in lEx:
                print(sLine.strip())
                # clog.error(sLine)
        # endif
        _print("===================================================================")
        _print("")

    # enddef


# endclass


###########################################################################################
class CAnyError_Message(CAnyError):
    def __init__(self, *, sMsg, xChildEx=None):

        super().__init__(sMsg=sMsg, sType="message", xData=sMsg, xChildEx=xChildEx)

    # enddef

    def __str__(self):
        return self.ToString()

    # enddef


# endclass


############################################################################################
class CAnyError_TaskMessage(CAnyError):
    def __init__(self, *, sTask, sMsg, xChildEx=None):

        sMessage = f"{sTask}:\n{sMsg}"
        super().__init__(
            sMsg=sMessage,
            sType="func-message",
            xData=sTask,
            xSelect=sMsg,
            xChildEx=xChildEx,
        )

    # enddef

    def __str__(self):
        return self.ToString()

    # enddef


# endclass
