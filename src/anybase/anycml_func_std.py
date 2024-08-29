#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: Thursday, October 22nd 2020, 4:26:28 pm
# Author: Christian Perwass
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
import pyjson5
import random
import numpy as np
from glob import glob
from pathlib import Path
from typing import Any

import ison
from . import config
from . import file
from . import path
from ison.core.cls_parser_error import (
    CParserError,
    CParserError_Message,
    CParserError_DictSel,
    CParserError_ListSel,
    CParserError_ProcArgStr,
    CParserError_ProcFunc,
    CParserError_ProcFuncArgs,
    CParserError_ProcKey,
    CParserError_ProcLambda,
    CParserError_ProcLambdaArgs,
    CParserError_ProcRefPath,
    CParserError_ProcStr,
    CParserError_StrMatch,
    CParserError_KeyStrMatch,
    CParserError_FuncMessage,
)

g_dicImport = {}


def tooltip(sTooltip):
    def inner(func):
        func.tooltip = sTooltip
        return func

    return inner


################################################################################
@tooltip("[Todo]")
def DictPathList(_xParser, _lArgs, _lArgIsProc, *, sFuncName):

    if not all(_lArgIsProc):
        return None, False
    # endif

    iArgCnt = len(_lArgs)

    if iArgCnt == 0 or iArgCnt > 1:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMSg="Function {0} expects exactly 1 argument but {1} were given".format(sFuncName, iArgCnt),
        )
    # endif

    if not isinstance(_lArgs[0], dict):
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function 'dict_path_list' expects a dictionary as input",
        )
    # endif

    return config.GetDictPaths(_lArgs[0]), False


# enddef


################################################################################
@tooltip("[Todo]")
def DictPathDict(_xParser, _lArgs, _lArgIsProc, *, sFuncName):

    if not all(_lArgIsProc):
        return None, False
    # endif

    iArgCnt = len(_lArgs)

    if iArgCnt == 0 or iArgCnt > 3:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function {0} expects between 1 and 3 arguments but {1} were given".format(sFuncName, iArgCnt),
        )
    # endif

    if not isinstance(_lArgs[0], dict):
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function '{0}' expects a dictionary as first argument.".format(sFuncName),
        )
    # endif

    if iArgCnt > 1 and not isinstance(_lArgs[1], str):
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function '{0}' expects a string as second argument.".format(sFuncName),
        )
    # endif

    if iArgCnt > 2 and not (isinstance(_lArgs[2], str) or isinstance(_lArgs[2], list)):
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function '{0}' expects a string or list as third argument.".format(sFuncName),
        )
    # endif

    lKeyPath = []
    if iArgCnt > 1:
        sKeyPath = _lArgs[1]
        lKeyPath = ison.text.SplitVarPath(sKeyPath)
    # endif

    if iArgCnt > 2:
        if isinstance(_lArgs[2], str):
            lPaths = [_lArgs[2]]
        else:
            lPaths = _lArgs[2]
        # endif
    else:
        lPaths = config.GetDictPaths(_lArgs[0])
    # endif

    xResult = {}
    for sPath in lPaths:
        xEl = config.GetDictValue(_lArgs[0], sPath, Any, bAllowKeyPath=True)
        # xEl = config.GetElementAtPath(_lArgs[0], sPath)
        if len(lKeyPath) > 0:
            sKey = ison.text.ToString(_xParser.ProcessRefPath(xEl, lKeyPath, 0))
        else:
            sKey = sPath
        # endif
        xResult[sKey] = xEl
    # endfor

    return xResult, False


# enddef


################################################################################
@tooltip("Updates dictionaries. Obsolete, use $union{} instead")
def DictUpdate(_xParser, _lArgs, _lArgIsProc, *, sFuncName):

    if not all(_lArgIsProc):
        return None, False
    # endif

    iArgCnt = len(_lArgs)

    if iArgCnt == 0:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function {0} expects at least 1 argument but 0 were given".format(sFuncName),
        )
    # endif

    xResult = {}
    for iArgIdx in range(iArgCnt):
        dicVal = _lArgs[iArgIdx]
        if not isinstance(dicVal, dict):
            raise CParserError_FuncMessage(
                sFunc=sFuncName,
                sMsg="Argument {0} of function '{1}' is not a dictionary".format(iArgIdx + 1, sFuncName),
            )
        # endif
        xResult.update(dicVal)
    # endfor

    return xResult, False


# enddef


################################################################################
def _RandomSelectInDict(_dicVal):

    dicSel = {}
    for sKey in _dicVal:
        xValue = _dicVal[sKey]
        if isinstance(xValue, list):
            dicSel[sKey] = random.choice(xValue)

        elif isinstance(xValue, dict):
            dicSel[sKey] = _RandomSelectInDict(xValue)

        else:
            dicSel[sKey] = xValue

        # endif
    # endfor

    return dicSel


# enddef


################################################################################
@tooltip("Randomly selects from dictionary. Obsolete, use $rand.zwicky{} instead")
def DictRndDict(_xParser, _lArgs, _lArgIsProc, *, sFuncName):

    if not all(_lArgIsProc):
        return None, False
    # endif

    iArgCnt = len(_lArgs)

    if iArgCnt != 1:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function {0} expects at exactly 1 argument but {1} were given".format(sFuncName, iArgCnt),
        )
    # endif

    dicVal = _lArgs[0]
    if not isinstance(dicVal, dict):
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="The argument of function '{0}' is not a dictionary".format(sFuncName),
        )
    # endif

    dicProc, bIsProc = _xParser.InnerProcess(dicVal)
    xResult = _RandomSelectInDict(dicProc)

    return xResult, False


# enddef


################################################################################
@tooltip("Get directory listing. Obsolete, use $dir{} instead.")
def DirectoryList(_xParser, _lArgs, _lArgIsProc, *, sFuncName):

    if not all(_lArgIsProc):
        return None, False
    # endif

    iArgCnt = len(_lArgs)

    if iArgCnt != 1:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function {0} expects exactly 1 argument but {1} were given".format(sFuncName, iArgCnt),
        )
    # endif

    sPath = _lArgs[0]
    if not isinstance(sPath, str):
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Function {0}: First parameter has to be a string".format(sFuncName),
        )
    # endif

    lPaths = glob(path.NormPath(sPath), recursive=True)
    if lPaths is not None:
        xResult = [path.NormPath(x) for x in lPaths]
    else:
        xResult = None
    # endif

    return xResult, False


# enddef


################################################################################
@tooltip("Evaluates the argument as python code")
def EvalPython(_xParser, _lArgs, _lArgIsProc, *, sFuncName):

    if not all(_lArgIsProc):
        return None, False
    # endif

    iArgCnt = len(_lArgs)

    if iArgCnt != 1:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Python interpreter function reequires exactly one argument, {0} are given".format(iArgCnt),
        )
    # endif

    if isinstance(_lArgs[0], list):
        sCmd = "".join(sum(_lArgs, []))
    else:
        sCmd = _lArgs[0]

    if not isinstance(sCmd, str):
        raise CParserError_FuncMessage(sFunc=sFuncName, sMsg="Python interpreter expects a string as argument")
    # endif
    sCmd = sCmd.strip()

    try:
        xResult = eval(
            sCmd,
            {
                "rnd": random,
                "random": random,
                "np": np,
                "numpy": np,
                "dicVar": _xParser.GetVarData(),
            },
        )

    except Exception as xEx:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Error executing python code: {0}".format(sCmd),
            xChildEx=xEx,
        )
    # endtry

    if xResult is None:
        xResult = "python eval('{0}')".format(sCmd)
    # endif

    return xResult, False


# enddef


################################################################################
@tooltip("Encodes the argument as json")
def Json(_xParser, _lArgs, _lArgIsProc, *, sFuncName):

    if not all(_lArgIsProc):
        return None, False
    # endif

    iArgCnt = len(_lArgs)

    if iArgCnt != 1:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="JSON function reequires exactly one argument, {0} are given".format(iArgCnt),
        )
    # endif

    xResult = pyjson5.encode(_lArgs[0])

    return xResult, False


# enddef


################################################################################
@tooltip(
    "Substitutes with the file contents of the file passed as string. "
    "The second optional argument specifies the expected DTI"
    "If the path contains wildcards, the first matching path is used"
)
def Import(_xParser, _lArgs, _lArgIsProc, *, sFuncName, funcGetCustomVarsFromPath=None):
    global g_dicImport

    if not all(_lArgIsProc):
        return None, False
    # endif

    if _xParser.IsIgnoreImport():
        return None, False
    # endif

    iArgCnt = len(_lArgs)

    if iArgCnt < 1 or iArgCnt > 2:
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Import function requires one or two arguments, {0} are given".format(iArgCnt),
        )
    # endif

    sImportPath = None
    dicVarData = _xParser.GetVarData()
    if "@loc" in dicVarData:
        sImportPath = dicVarData["@loc"].get("path")
    # endif

    if sImportPath is None:
        sImportPath = _xParser.GetImportPath()
    # endif

    if sImportPath is None:
        sFpImport = path.NormPath(_lArgs[0])
    else:
        sFpImport = path.NormPath(os.path.join(sImportPath, _lArgs[0]))
    # endif

    pathFile = Path(sFpImport)
    if not pathFile.is_absolute():
        raise CParserError_FuncMessage(
            sFunc=sFuncName,
            sMsg="Cannot create absolute file path for in import function: {0}".format(sFpImport),
        )
    # endif

    if "*" in pathFile.as_posix():
        # Resolve wildcards * and use the first hit to enable rudimentariy wildcard support
        lPaths = glob(pathFile.as_posix())
        if len(lPaths) == 0:
            raise CParserError_FuncMessage(
                sFunc=sFuncName,
                sMsg=f"No files found for pattern: {pathFile.as_posix()}",
            )
        # endif
        pathImport = Path(lPaths[0])
    else:
        pathImport = path.ProvideReadFilepathExt(pathFile, [".json", ".json5", ".ison"], bDoRaise=True)
    # endif

    if pathImport.as_posix() in g_dicImport:
        xResult = g_dicImport.get(pathImport.as_posix())
    else:
        try:
            if iArgCnt == 2:
                sFpImport = pathImport.parent.as_posix()
                if funcGetCustomVarsFromPath is not None:
                    dicCustomVars = funcGetCustomVarsFromPath(sFpImport)
                else:
                    dicCustomVars = {}
                # endif

                xResult = config.Load(
                    pathImport,
                    sDTI=_lArgs[1],
                    bAddPathVars=True,
                    dicCustomVars=dicCustomVars,
                )
            else:
                xResult = file.LoadJson(pathImport.as_posix())
            # endif
        except Exception as xEx:
            raise CParserError_FuncMessage(
                sFunc=sFuncName,
                sMsg="Error importing '{0}' from path: {1}".format(pathImport.name, pathImport.parent),
                xChildEx=xEx,
            )
        # endtry

        g_dicImport[pathImport.as_posix()] = xResult
    # endif

    return xResult, False


# enddef


################################################################################
__ison_functions__ = {
    "dict_path_list": DictPathList,
    "dict_path_dict": DictPathDict,
    "dict_update": DictUpdate,
    "dict_rnd_sel": DictRndDict,
    "dir_list": DirectoryList,
    "py": EvalPython,
    "json": Json,
    "import": Import,
}
