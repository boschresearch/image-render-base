#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Author: Christian Perwass (CR/ADI2.1)
# <LICENSE id="Apache-2.0">
#
#   Image-Render Base Functions module
#   Copyright 2023 Robert Bosch GmbH and its subsidiaries
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

from typing import Optional, Callable


class CProcessHandler:
    def __init__(
        self,
        *,
        _funcPreStart: Optional[Callable[[list], None]] = None,
        _funcPostStart: Optional[Callable[[list, int], None]] = None,
        _funcStdOut: Optional[Callable[[str], None]] = None,
        _funcEnded: Optional[Callable[[int, str], None]] = None,
    ):
        self._lFuncPreStart: list[Callable[[list], None]] = []
        self._lFuncPostStart: list[Callable[[list, int], None]] = []
        self._lFuncStdOut: list[Callable[[str], None]] = []
        self._lFuncEnded: list[Callable[[int, str], None]] = []

        self.AddHandlerPreStart(_funcPreStart)
        self.AddHandlerPostStart(_funcPostStart)
        self.AddHandlerStdOut(_funcStdOut)
        self.AddHandlerEnded(_funcEnded)

    # enddef

    @property
    def bPreStartAvailable(self) -> bool:
        return len(self._lFuncPreStart) > 0

    # enddef

    @property
    def bPostStartAvailable(self) -> bool:
        return len(self._lFuncPostStart) > 0

    # enddef

    @property
    def bStdOutAvailable(self) -> bool:
        return len(self._lFuncStdOut) > 0

    # enddef

    @property
    def bEndedAvailable(self) -> bool:
        return len(self._lFuncEnded) > 0

    # enddef

    def PreStart(self, *args):
        funcX: Callable[[list], None] = None
        for funcX in self._lFuncPreStart:
            funcX(*args)
        # endfor

    # enddef

    def PostStart(self, *args):
        funcX: Callable[[list, int], None] = None
        for funcX in self._lFuncPostStart:
            funcX(*args)
        # endfor

    # enddef

    def StdOut(self, *args):
        funcX: Callable[[str], None] = None
        for funcX in self._lFuncStdOut:
            funcX(*args)
        # endfor

    # enddef

    def Ended(self, *args):
        funcX: Callable[[int, str], None] = None
        for funcX in self._lFuncEnded:
            funcX(*args)
        # endfor

    # enddef

    # ############################################################################
    def AddHandlerPreStart(self, _funcPreStart: Callable[[list], None]):
        if _funcPreStart is not None:
            self._lFuncPreStart.append(_funcPreStart)
        # endif

    # enddef

    # ############################################################################
    def AddHandlerPostStart(self, _funcPostStart: Callable[[list, int], None]):
        if _funcPostStart is not None:
            self._lFuncPostStart.append(_funcPostStart)
        # endif

    # enddef

    # ############################################################################
    def AddHandlerStdOut(self, _funcStdOut: Callable[[str], None]):
        if _funcStdOut is not None:
            self._lFuncStdOut.append(_funcStdOut)
        # endif

    # enddef

    # ############################################################################
    def AddHandlerEnded(self, _funcEnded: Callable[[int, str], None]):
        if _funcEnded is not None:
            self._lFuncEnded.append(_funcEnded)
        # endif

    # enddef


# enddef
