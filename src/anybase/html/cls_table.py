#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \ipy\cls_htmltable.py
# Created Date: Tuesday, February 22nd 2022, 8:45:04 am
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

from typing import Optional
from .cls_render_base import CHtmlRenderBase

from anybase import config

#######################################################################
class CHtmlTable(CHtmlRenderBase):

    ###################################################################
    def __init__(self, *, iRows: int, iCols: int, dicStyle: Optional[dict] = None):

        # Member variable declaration
        self._bHasRowHeader: bool = None
        self._bHasColHeader: bool = None
        self._sStyleColHeader: str = None
        self._sStyleRowHeader: str = None

        self._iRows: int = None
        self._iCols: int = None
        self._bTransposed: bool = None

        self._aData: list[list[str]] = None

        self._iIndentTabCnt: int = None
        self._sIndentTab: str = None
        self._sIndent: str = None

        # Class initialization
        if iRows <= 0 or iCols <= 0:
            raise RuntimeError(
                "Number of rows and cols of table has to be greater than zero"
            )
        # endif

        if isinstance(dicStyle, dict):
            self._bHasColHeader = dicStyle.get("bHasColHeader", False)
            self._bHasRowHeader = dicStyle.get("bHasRowHeader", False)
            self._sStyleColHeader = dicStyle.get("sStyleColHeader", None)
            self._sStyleRowHeader = dicStyle.get("sStyleRowHeader", None)
        else:
            self._bHasRowHeader = False
            self._bHasColHeader = False
            self._sStyleColHeader = None
            self._sStyleRowHeader = None
        # endif

        self._iRows = iRows
        self._iCols = iCols
        self._bTransposed = False

        self._aData = [["" for iCol in range(iCols)] for iRow in range(iRows)]

        self._iIndentTabCnt = 4
        self._sIndentTab = " " * self._iIndentTabCnt
        self._InitHtml()

    # enddef

    ###################################################################
    def AddHtml(self, iRowIdx, iColIdx, sHtml):
        if (
            iRowIdx < 0
            or iRowIdx >= self._iRows
            or iColIdx < 0
            or iColIdx >= self._iCols
        ):
            raise RuntimeError(
                "Cell position ({}, {}) "
                "out of bounds ([0, {}], [0, {}])".format(
                    iRowIdx, iColIdx, self._iRows - 1, self._iCols - 1
                )
            )
        # endif

        self._aData[iRowIdx][iColIdx] = sHtml

    # enddef

    ###################################################################
    def GetIndentLen(self):
        return len(self._sIndent)

    # enddef

    ###################################################################
    def _InitHtml(self, iIndent=0):
        if iIndent > 0:
            self._sIndent = " " * iIndent
        else:
            self._sIndent = ""
        # endif

        self._sHtml = ""

    # enddef

    ###################################################################
    def _AddIndent(self):
        self._sIndent += self._sIndentTab

    # enddef

    ###################################################################
    def _SubIndent(self):
        if len(self._sIndent) > self._iIndentTabCnt:
            self._sIndent = self._sIndent[: -self._iIndentTabCnt]
        else:
            self._sIndent = ""
        # endif

    # enddef

    ###################################################################
    def _StartTable(self):
        self._sHtml += self._sIndent + "<table>\n"
        self._AddIndent()

    # enddef

    ###################################################################
    def _EndTable(self):
        self._SubIndent()
        self._sHtml += self._sIndent + "</table>\n"

    # enddef

    ###################################################################
    def _StartRow(self):
        self._sHtml += self._sIndent + "<tr>\n"
        self._AddIndent()

    # enddef

    ###################################################################
    def _EndRow(self):
        self._SubIndent()
        self._sHtml += self._sIndent + "</tr>\n"

    # enddef

    ###################################################################
    def _AddCol(self, sHtml):
        self._sHtml += self._sIndent + "<td>{}</td>\n".format(sHtml)

    # enddef

    ###################################################################
    def _AddHead(self, sHtml, bColumn=True):
        if bColumn is True:
            sStyle = self._GetColHeaderStyle()
        else:
            sStyle = self._GetRowHeaderStyle()
        # endif

        if isinstance(sStyle, str):
            sHead = '<th style="{}">{}</th>\n'.format(sStyle, sHtml)
        else:
            sHead = "<th>{}</th>\n".format(sHtml)
        # endif

        self._sHtml += self._sIndent + sHead

    # enddef

    ###################################################################
    def _GetDataRow(self, iIdx):
        return self._aData[iIdx]

    # enddef

    ###################################################################
    def _GetDataCol(self, iIdx):
        return [x[iIdx] for x in self._aData]

    # enddef

    ###################################################################
    def _GetRow(self, iIdx):
        if self._bTransposed is True:
            return self._GetDataCol(iIdx)
        else:
            return self._GetDataRow(iIdx)
        # enddef

    # enddef

    ###################################################################
    def _GetCol(self, iIdx):
        if self._bTransposed is True:
            return self._GetDataRow(iIdx)
        else:
            return self._GetDataCol(iIdx)
        # enddef

    # enddef

    ###################################################################
    def _HasColHeader(self):
        if self._bTransposed is True:
            return self._bHasRowHeader
        else:
            return self._bHasColHeader
        # endif

    # enddef

    ###################################################################
    def _HasRowHeader(self):
        if self._bTransposed is True:
            return self._bHasColHeader
        else:
            return self._bHasRowHeader
        # endif

    # enddef

    ###################################################################
    def _GetRowHeaderStyle(self):
        return self._sStyleRowHeader

    # enddef

    ###################################################################
    def _GetColHeaderStyle(self):
        return self._sStyleColHeader

    # enddef

    ###################################################################
    def GetRowCnt(self):
        return self._iRows if not self._bTransposed else self._iCols

    # enddef

    ###################################################################
    def GetColCnt(self):
        return self._iCols if not self._bTransposed else self._iRows

    # enddef

    ###################################################################
    def Transpose(self):
        self._bTransposed = not self._bTransposed

    # enddef

    ###################################################################
    def SetTranspose(self, _bTransposed):
        self._bTransposed = _bTransposed

    # enddef

    ###################################################################
    def Render(self, **kwargs):

        sWhere = "render html table"
        bShowColHeader = config.GetDictValue(
            kwargs, "bShowColHeader", bool, xDefault=True, sWhere=sWhere
        )
        bShowRowHeader = config.GetDictValue(
            kwargs, "bShowRowHeader", bool, xDefault=True, sWhere=sWhere
        )
        iIndent = config.GetDictValue(kwargs, "iIndent", int, xDefault=0, sWhere=sWhere)
        iRowStart = config.GetDictValue(
            kwargs, "iRowStart", int, xDefault=None, bOptional=True, sWhere=sWhere
        )
        iRowCount = config.GetDictValue(
            kwargs, "iRowCount", int, xDefault=None, bOptional=True, sWhere=sWhere
        )

        return self.RenderTable(
            bShowColHeader=bShowColHeader,
            bShowRowHeader=bShowRowHeader,
            iIndent=iIndent,
            iRowStart=iRowStart,
            iRowCount=iRowCount,
        )

    # enddef

    ###################################################################
    def RenderTable(
        self,
        bShowColHeader=True,
        bShowRowHeader=True,
        iIndent=0,
        iRowStart=None,
        iRowCount=None,
    ):

        self._InitHtml(iIndent=iIndent)
        self._StartTable()

        iRowIdxCount = iRowCount if iRowCount is not None else self.GetRowCnt()
        iRowIdxStart = iRowStart if iRowStart is not None else 0

        # Create header row
        if self._HasColHeader() is True:
            if bShowColHeader is True:
                self._StartRow()
                lRow = self._GetRow(0)

                iColIdxStart = 0
                if self._HasRowHeader():
                    if bShowRowHeader is True:
                        self._AddHead(lRow[0])
                    # endif
                    iColIdxStart = 1
                # endif

                for sCol in lRow[iColIdxStart:]:
                    self._AddHead(sCol, bColumn=True)
                # endfor
                self._EndRow()
            # endif
            iRowIdxStart += 1
        # endif

        iRowIdxEnd = min(iRowIdxStart + iRowIdxCount, self.GetRowCnt())
        for iRowIdx in range(iRowIdxStart, iRowIdxEnd):
            lRow = self._GetRow(iRowIdx)
            self._StartRow()
            iColIdxStart = 0
            if self._HasRowHeader():
                if bShowRowHeader is True:
                    self._AddHead(lRow[0])
                # endif
                iColIdxStart = 1
            # endif

            for sCol in lRow[iColIdxStart:]:
                self._AddCol(sCol)
            # endfor
            self._EndRow()
        # endfor rows

        self._EndTable()
        return self._sHtml

    # enddef


# endclass
