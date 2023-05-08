#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \ipy\cls_htmlpage.py
# Created Date: Wednesday, February 23rd 2022, 7:11:17 am
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
from typing import Optional, ForwardRef

THtmlRenderBase = ForwardRef("CHtmlRenderBase")

#######################################################################
class CHtmlRenderBase:
    @property
    def sHtml(self) -> str:
        return self._sHtml

    ###################################################################
    def __init__(self, _xHtmlRenderBase: Optional[THtmlRenderBase] = None):
        self._sHtml: str = None

        if isinstance(_xHtmlRenderBase, CHtmlRenderBase):
            self._sHtml = _xHtmlRenderBase.sHtml
        else:
            self.Clear()
        # endif

    # enddef

    ###################################################################
    def __str__(self):
        return self.sHtml

    # enddef

    ###################################################################
    def Clear(self):
        self._sHtml = ""

    # enddef

    ###################################################################
    def Render(self, **kwargs):
        return self._sHtml

    # enddef

    ###################################################################
    def Header(self, _sText, iLevel=1):
        self._sHtml += "<h{1}>{0}</h{1}>\n".format(_sText, iLevel)

    # enddef

    ###################################################################
    def Line(self, _sText):
        self._sHtml += _sText + "\n"

    # enddef

    ###################################################################
    def Paragraph(self, _sText):
        self._sHtml += f"<p>{_sText}</p>\n"

    # enddef


# endclass
