#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_config_base.py
# Created Date: Thursday, March 23rd 2023, 2:47:21 pm
# Author: Christian Perwass
# <LICENSE id="Apache-2.0">
#
#   Image-Render Standard Actions module
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

import copy
from typing import Union, Callable
from pathlib import Path

from . import path
from . import config
from .cls_any_error import CAnyError_Message


# Configuration base class, supporting sDTI and sId tags.
class CConfigBase:
    def __init__(self, _sDti: str, *, _funcInitFromCfg: Callable = None):
        self._sDti: str = _sDti
        self._lDtiType: list[str] = None
        self._lDtiVersion: tuple[int, int] = None
        self._sId: str = None

        self._dicCfg: dict = None

        dicRes = config.SplitDti(self._sDti)
        self._lDtiType = dicRes["lType"]
        self._lDtiVersion = dicRes["lVersion"]

        self._funcInitFromCfg: Callable = _funcInitFromCfg

    # enddef

    @property
    def sDti(self) -> str:
        return self._sDti

    # enddef

    @property
    def lDtiType(self) -> list[str]:
        return self._lDtiType

    # enddef

    @property
    def lDtiVersion(self) -> tuple[int, int]:
        return self._lDtiVersion

    # enddef

    @property
    def sId(self) -> str:
        return self._sId

    # enddef

    @property
    def dicConfig(self) -> dict:
        return self._dicCfg

    # enddef

    def _Init(self):
        self._sId = self._dicCfg.get("sId")
        if self._sId is None:
            raise RuntimeError("Configuration data has no element 'sId'")
        # endif

    # endif

    def FromFile(
        self,
        _xPathFile: Union[str, list, tuple, Path],
        *,
        _bReplacePureVars: bool = True,
        _bAddPathVars: bool = False,
        _bDoThrow: bool = True,
        _dicCustomVars: dict = None,
    ):

        self._dicCfg = config.Load(
            _xPathFile,
            sDTI=self._sDti,
            bReplacePureVars=_bReplacePureVars,
            bAddPathVars=_bAddPathVars,
            bDoThrow=_bDoThrow,
            dicCustomVars=_dicCustomVars,
        )

        try:
            self._Init()
            if self._funcInitFromCfg is not None:
                self._funcInitFromCfg()
            # endif
        except Exception as xEx:
            pathFile = path.MakeNormPath(_xPathFile)
            raise CAnyError_Message(sMsg=f"Error loading configuration file: {(pathFile.as_posix())}", xChildEx=xEx)
        # endtry

    # enddef FromFile()

    def FromDict(self, _dicData: dict):
        config.AssertConfigType(_dicData, self._sDti)
        self._dicCfg = copy.deepcopy(_dicData)
        self._Init()

    # enddef FromDict()


# endclass
