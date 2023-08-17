###
# Author: Christian Perwass (CR/ADI2.1)
# <LICENSE id="Apache-2.0">
#
#   Image-Render Automation Functions module
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


class CProcessOutput:
    def __init__(self):
        self._iNextLine: int = 0
        self._lLines: list[str] = []

    # enddef

    def __iter__(self):
        return self

    # enddef

    def __next__(self):
        if not self.bHasNewLines:
            raise StopIteration
        # endif
        sLine = self._lLines[self._iNextLine]
        self._iNextLine += 1
        return sLine

    # enddef

    def __getitem__(self, iIdx: int) -> str:
        return self._lLines[iIdx]

    # enddef

    def __len__(self) -> int:
        return len(self._lLines)

    # enddef

    @property
    def bHasNewLines(self) -> bool:
        return self._iNextLine < len(self._lLines)

    # enddef

    @property
    def iNextLine(self) -> int:
        return self._iNextLine

    # enddef

    def Clear(self):
        self._lLines = []
        self._iNextLine = 0

    # enddef

    def Rewind(self, iLines: int = 0):
        if iLines <= 0:
            self._iNextLine = 0
        else:
            self._iNextLine = max(0, self._iNextLine - iLines)
        # endif

    # enddef

    def AddLine(self, _sLine: str):
        self._lLines.append(_sLine)

    # enddef


# endclass
