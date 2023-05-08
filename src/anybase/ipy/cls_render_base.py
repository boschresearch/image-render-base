#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_cathipy_action.py
# Created Date: Tuesday, August 10th 2021, 3:41:16 pm
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

from typing import Optional, ForwardRef, Callable

from pathlib import Path
from IPython.display import Image, Video, JSON, display
from IPython.display import Markdown, HTML

TIPyRenderBase = ForwardRef("CIPyRenderBase")


def RenderImageStd(sFpImage: str, iWidth: int, iHeight: int):
    return Image(filename=sFpImage, width=iWidth, height=iHeight)


# enddef


class CIPyRenderBase:
    @property
    def lRichObjects(self):
        return self._lRichObjects

    ##########################################################################
    def __init__(self, _xIPyRenderBase: Optional[TIPyRenderBase] = None):
        self.Clear()
        if _xIPyRenderBase is not None:
            self._lRichObjects = _xIPyRenderBase.lRichObjects.copy()
            self._bContainsImage = _xIPyRenderBase.bContainsImage
            self._bContainsVideo = _xIPyRenderBase.bContainsVideo
        # endif

        self._dicImgRender = {".png": RenderImageStd, ".jpg": RenderImageStd}

    # enddef

    ##########################################################################
    def Clear(self):
        self._lRichObjects = []
        self._bContainsVideo = False
        self._bContainsImage = False

    # enddef

    ##########################################################################
    def RegisterImageRenderer(self, *, sFileSuffix: str, funcImageRenderer: Callable):
        self._dicImgRender[sFileSuffix] = funcImageRenderer

    # enddef

    ##########################################################################
    def Text(self, _sText):
        self._lRichObjects.append(Markdown(_sText))

    # enddef

    ##########################################################################
    def HTML(self, _sText):
        self._lRichObjects.append(HTML(_sText))

    # enddef

    ##########################################################################
    def Json(self, _sText):
        self._lRichObjects.append(JSON(_sText, expanded=True))

    # enddef

    ##########################################################################
    def Image(self, *, sFpImage, iWidth=None, iHeight=None):

        self._bContainsImage = True
        pathImg = Path(sFpImage)
        sExt = pathImg.suffix

        funcImgRender = self._dicImgRender.get(sExt)
        if funcImgRender is None:
            self.Text(f"No image renderer available for file type '{sExt}': {sFpImage}")
        else:
            self._lRichObjects.append(funcImgRender(sFpImage, iWidth, iHeight))
        # endif

    # enddef

    ##########################################################################
    def Video(self, *, sFpVideo, iWidth=None, iHeight=None):
        self._bContainsVideo = True
        self._lRichObjects.append(Video(sFpVideo, width=iWidth, height=iHeight))

    # enddef

    ##########################################################################
    def Object(self, _xObject: TIPyRenderBase):
        self._lRichObjects.extend(_xObject.lRichObjects)

    # enddef

    ##########################################################################
    def Display(self):

        if self._bContainsVideo:
            self._lRichObjects.insert(
                0,
                Markdown(
                    "> Video display does not work in VSCode. "
                    "This is a known limitation."
                ),
            )
        # endif

        display(*self._lRichObjects)
        self.Clear()

    # enddef


# endclass
