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

from .cls_render_base import CHtmlRenderBase


#######################################################################
class CHtmlPage(CHtmlRenderBase):

    c_sStyle: str = """
    body {
        background-color: rgb(59, 59, 59);
        color: rgb(182, 179, 173);
    }

    a {
        color:rgb(115, 116, 182)
    }

    h1 {
        color: Azure;
        font-weight: bold;
    }

    code {
        color: Bisque;
    }

    th {
        padding: 5px;
        padding-left: 10px;
    }

    table td {
        text-align: center;
    }

    table tr:nth-child(even) {
        background-color: rgb(71, 71, 71);
    }
    table tr:nth-child(even) table {
        background-color: rgb(87, 87, 87);
        padding-right: 10px;
    }
    """

    @property
    def sPage(self) -> str:
        return self._sPage

    ###################################################################
    def __init__(self):
        self._sPage: str = None

        super().__init__()
        self._sStyle: str = self.c_sStyle

        self.Clear()

    # enddef

    ###################################################################
    def Clear(self):
        super().Clear()
        self._sPage = ""

    # enddef

    ###################################################################
    def Render(self, **kwargs):
        self._sPage = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<style>\n"
            "{}\n"
            "</style>\n"
            "<body>\n"
            "{}\n"
            "</body>\n"
            "</html>\n"
        ).format(self._sStyle, self._sHtml)

        return self.sPage

    # enddef


# endclass
