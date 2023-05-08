#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \assertion.py
# Created Date: Wednesday, May 25th 2022, 10:49:53 am
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

import inspect
import types
import typing
from typing import Any, Iterable, Union, Optional, TypeVar
from anybase.cls_any_error import CAnyError, CAnyError_Message

###########################################################################################
# Global module variable indicates whether assertions are to be tested or not.
# By default assertions are ignored.
g_bEnabled: bool = False


###########################################################################################
def Enable(_bEnable: bool = True) -> None:
    global g_bEnabled
    g_bEnabled = _bEnable


# endddef


###########################################################################################
def IsEnabled() -> bool:
    global g_bEnabled
    return g_bEnabled


# enddef


###########################################################################################
def _GetCallingFunction(_xFrame: types.FrameType) -> types.FunctionType:
    import gc

    xCode = _xFrame.f_code
    xGlobs = _xFrame.f_globals
    funcCaller = None

    for funcX in gc.get_referrers(xCode):
        if (
            inspect.isfunction(funcX)
            and getattr(funcX, "__code__", None) is xCode
            and getattr(funcX, "__globals__", None) is xGlobs
        ):
            funcCaller = funcX
            break
        # endif
    # endfor

    return funcCaller


# enddef


###########################################################################################
def _TestTypeCln(_xValue: Any, _clnType: Iterable) -> typing.Union[bool, None]:

    bHasType = False
    bIgnoreType = False
    for typeY in _clnType:
        bTest = _TestType(_xValue, typeY)
        if bTest is True:
            bHasType = True
            break
        # endif
        if bTest is None:
            bIgnoreType = True
        # endif
    # endfor

    if bHasType is True:
        return True
    elif bIgnoreType is True:
        return None
    else:
        return False
    # endif


# enddef

###########################################################################################
def _TestType(_xValue: Any, _typeX: Union[type, list[type]]) -> typing.Union[bool, None]:

    # Check for type list
    if type(_typeX) == list:
        return _TestTypeCln(_xValue, _typeX)
    # endif

    # Ignore generic TypeVar variables
    if isinstance(_typeX, TypeVar):
        return None
    # endif

    # If type has a list of alternative types then check for any of them
    try:
        bIsUnionType = isinstance(_typeX, typing._UnionGenericAlias)
    except Exception:
        bIsUnionType = False
    # endtry

    if bIsUnionType is True:
        tTypes = typing.get_args(_typeX)
        if len(tTypes) > 0:
            return _TestTypeCln(_xValue, tTypes)
        # endif
    # endif

    try:
        bIsCallable = isinstance(_typeX, typing._CallableGenericAlias)
    except Exception:
        bIsCallable = False
    # endtry

    # Assume callables to be of type "function" and ignore their arguments
    if bIsCallable is True:
        return isinstance(_xValue, types.FunctionType)
    # endif

    try:
        # Test type
        return isinstance(_xValue, _typeX)
    except Exception:
        # If type cannot be tested with isinstance(), then ignore type
        return None
    # endtry


# enddef

###########################################################################################
def IsOfType(
    _xValue: Any,
    _typeX: type,
    sMsg: Optional[str] = None,
    xCallFrame: Optional[types.FrameType] = None,
    sVarName: str = "Value",
    bForce=False,
) -> None:

    if not IsEnabled() and bForce is False:
        return
    # endif

    if _TestType(_xValue, _typeX) is False:
        if xCallFrame is None:
            xCallFrame = inspect.currentframe().f_back
        # endif
        (sFilename, iLineNumber, sFunctionName, lLines, iIndex) = inspect.getframeinfo(xCallFrame)
        sWhere = CAnyError.ListToString(
            [
                "Function: {}".format(sFunctionName),
                "File: {}".format(sFilename),
                "Line/Position: {}/{}".format(iLineNumber, iIndex),
            ]
        )
        if sMsg is None:
            if hasattr(_typeX, "__name__") and hasattr(type(_xValue), "__name__"):
                sMsg = "ASSERTION FAILED: {} is of type '{}', but expected type '{}'".format(
                    sVarName, type(_xValue).__name__, _typeX.__name__
                )
            else:
                sMsg = "ASSERTION FAILED: Invalid type"
            # endif
        # endif
        raise CAnyError_Message(sMsg=sMsg + sWhere)
    # endif


# enddef

###########################################################################################
def IsSame(
    _xValueA: Any,
    _xValueB: Any,
    sMsg: Optional[str] = None,
    xCallFrame: Optional[types.FrameType] = None,
    sVarName: str = "Value",
    bForce=False,
) -> None:

    if not IsEnabled() and bForce is False:
        return
    # endif

    sConversionMsg = None
    if isinstance(_xValueA, type(_xValueB)):
        if _xValueA == _xValueB:
            return True
    else:
        try:
            xValueConverted = type(_xValueB)(_xValueA)
            if xValueConverted == _xValueB:
                return
        except Exception as xEx:
            sConversionMsg = f"conversion of ({_xValueA} into type '{ type(_xValueB)}' raise exception '{xEx}'"
    # endif

    (sFilename, iLineNumber, sFunctionName, lLines, iIndex) = inspect.getframeinfo(xCallFrame)
    sWhere = CAnyError.ListToString(
        [
            "Function: {}".format(sFunctionName),
            "File: {}".format(sFilename),
            "Line/Position: {}/{}".format(iLineNumber, iIndex),
        ]
    )

    if sMsg is None:
        if type(_xValueA) != type(_xValueB):
            if hasattr(type(_xValueB), "__name__") and hasattr(type(_xValueA), "__name__"):
                sMsg = "ASSERTION FAILED: {} is of type '{}', but expected type '{}'".format(
                    sVarName, type(_xValueA).__name__, type(_xValueB).__name__
                )
            else:
                sMsg = "ASSERTION FAILED: Invalid type"
            # endif
        else:
            sMsg = f"ASSERTION FAILED: {sVarName} has value '{_xValueA}' but expected value '{_xValueB}'"
        # endif
    # endif

    if sConversionMsg is not None:
        sMsg += f"\nduring assertion raises another Exception:\n{sConversionMsg}"

    raise CAnyError_Message(sMsg=sMsg + sWhere)


# enddef

###########################################################################################
def FuncArgTypes(
    *,
    funcCaller=None,
    xCallFrame: Optional[types.FrameType] = None,
    bForce: Optional[bool] = False,
) -> None:

    if not IsEnabled() and bForce is False:
        return
    # endif

    if xCallFrame is None:
        xCallFrame = inspect.currentframe().f_back
    # endif

    if funcCaller is None:
        funcCaller = _GetCallingFunction(xCallFrame)
        if funcCaller is None:
            raise CAnyError_Message(sMsg="Cannot find calling function")
        # endif
    # endif

    sigFunc = inspect.signature(funcCaller)

    dicLocals = xCallFrame.f_locals

    # Only test arguments with "simple" types, i.e. avoid generics and type unions
    lArgs = [
        (x.name, dicLocals[x.name], x.annotation)
        for x in sigFunc.parameters.values()
        if x.annotation != inspect.Parameter.empty
    ]

    for tArg in lArgs:
        IsOfType(
            tArg[1],
            tArg[2],
            xCallFrame=xCallFrame,
            sVarName="Argument '{}'".format(tArg[0]),
        )
    # endfor


# enddef


###########################################################################################
def IsDict(_xValue: Any, sMsg: Optional[str] = None) -> None:
    IsOfType(_xValue, dict, sMsg=sMsg, xCallFrame=inspect.currentframe().f_back)


# enddef


###########################################################################################
def IsList(_xValue: Any, sMsg: Optional[str] = None) -> None:
    IsOfType(_xValue, list, sMsg=sMsg, xCallFrame=inspect.currentframe().f_back)


# enddef


###########################################################################################
def IsInt(_xValue: Any, sMsg: Optional[str] = None) -> None:
    IsOfType(_xValue, int, sMsg=sMsg, xCallFrame=inspect.currentframe().f_back)


# enddef


###########################################################################################
def IsFloat(_xValue: Any, sMsg: Optional[str] = None) -> None:
    IsOfType(_xValue, float, sMsg=sMsg, xCallFrame=inspect.currentframe().f_back)


# enddef


###########################################################################################
def IsBool(_xValue: Any, sMsg: Optional[str] = None) -> None:
    IsOfType(_xValue, bool, sMsg=sMsg, xCallFrame=inspect.currentframe().f_back)


# enddef


###########################################################################################
def IsTrue(_bValue: bool, sMsg: Optional[str] = None) -> None:
    IsSame(_bValue, True, sMsg=sMsg, xCallFrame=inspect.currentframe().f_back)


# enddef
