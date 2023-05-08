#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \pwrshell_01.py
# Created Date: Wednesday, May 25th 2022, 7:35:50 am
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


import os
import tempfile
import subprocess
from pathlib import Path

lCmdLines = [
    "write-host Hello",
    "write-host World",
    'write-host "$env:Hello"',
    "write-host $pwd.Path",
    "invoke-expression -Command \"& '$env:HOME\\Anaconda3\\shell\\condabin\\conda-hook.ps1'\"",
    "conda activate cath",
    "(Get-Command python).Path",
]

pathScript = None
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ps1") as xFile:
    pathScript = Path(xFile.name)
    xFile.write("\n".join(lCmdLines))
# endwith

print("Temporary File: {}".format(pathScript))

print("Running powershell with script...\n")

lCmd = ["powershell.exe", pathScript.as_posix()]
sCwd = "c:\\"

dicEnviron = os.environ.copy()
dicEnviron.update({"Hello": "Environment"})

procChild = subprocess.Popen(
    lCmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    shell=False,
    cwd=sCwd,
    universal_newlines=True,
    env=dicEnviron,
)

lLines = []
for sLine in iter(procChild.stdout.readline, ""):
    lLines.append(sLine)
    print(sLine, end="", flush=True)
# endfor

procChild.stdout.close()
iReturnCode = procChild.wait()

pathScript.unlink()
