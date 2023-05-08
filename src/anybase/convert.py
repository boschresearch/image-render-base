#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \convert.py
# Created Date: Saturday, February 19th 2022, 11:32:04 am
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
from collections.abc import Iterable
from .cls_any_error import CAnyError_Message


################################################################################
def _RaiseIfTrue(_bDoRaise: bool, *, _sMsg: str, _xChildEx=None):
    if _bDoRaise is True:
        raise CAnyError_Message(sMsg=_sMsg, xChildEx=_xChildEx)
    # endif

    return None


################################################################################
def ToTypename(xValue):

    if xValue is None:
        return "None"
    # endif

    sType = "unknown"

    if inspect.isclass(type(xValue)):
        sType = type(xValue).__name__

    elif isinstance(xValue, dict):
        sType = "dictionary"

    elif isinstance(xValue, list):
        sType = "list"

    elif isinstance(xValue, tuple):
        sType = "tuple"

    elif isinstance(xValue, str):
        sType = "string"

    elif isinstance(xValue, int):
        sType = "integer"

    elif isinstance(xValue, float):
        sType = "float"

    elif isinstance(xValue, bool):
        sType = "boolean"

    else:
        sType = str(type(xValue))
    # endif

    return sType


# enddef


#######################################################################
# Cast to integer
def ToInt(_xValue, iDefault=None, bDoRaise=True):
    try:
        iResult = int(_xValue)
    except Exception as xEx:
        if isinstance(iDefault, int):
            return iDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Error converting '{_xValue}' to integer.", _xChildEx=xEx)
    # endtry

    return iResult


# enddef

#######################################################################
# Cast to integer
def DictElementToInt(_dicData, _sElement, iDefault=None, bDoRaise=True):

    if iDefault is not None and not isinstance(iDefault, int):
        raise CAnyError_Message(sMsg=f"Default value is not an integer: {iDefault}")
    # endif

    if not isinstance(_dicData, dict):
        if isinstance(iDefault, int):
            return iDefault
        # endif
        raise CAnyError_Message(sMsg="No dictionary given")
    # endif

    xValue = _dicData.get(_sElement)
    if xValue is None:
        if iDefault is not None:
            return iDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Element '{_sElement}' not found")
    # enddef

    try:
        iResult = ToInt(xValue, iDefault=iDefault, bDoRaise=bDoRaise)

    except Exception as xEx:
        return _RaiseIfTrue(
            bDoRaise,
            _sMsg=f"Error converting element '{_sElement}' to integer. Value is: {xValue}",
            _xChildEx=xEx,
        )
    # endtry

    return iResult


# enddef


#######################################################################
# Cast to integer
def DictElementToIntList(_dicData, _sElement, iLen=None, lDefault=None, bDoRaise=True):

    if lDefault is not None:
        if not isinstance(lDefault, list):
            raise CAnyError_Message(sMsg=f"Default value is not a list: {lDefault}")
        elif isinstance(iLen, int) and len(lDefault) != iLen:
            raise CAnyError_Message(sMsg="Default list is of invalid length '{}': {}".format(len(lDefault), lDefault))
        # endif
    # endif

    if not isinstance(_dicData, dict):
        if isinstance(lDefault, list):
            return lDefault
        # endif
        raise CAnyError_Message(sMsg="No dictionary given")
    # endif

    lValue = _dicData.get(_sElement)
    if lValue is None:
        if isinstance(lDefault, list):
            return lDefault
        # endif
        if bDoRaise is True:
            raise CAnyError_Message(sMsg=f"Element '{_sElement}' not found")
        else:
            return None
        # endif
    # enddef

    if not isinstance(lValue, list):
        raise CAnyError_Message(sMsg=f"Element '{_sElement}' is not a list")
    # endif

    if isinstance(iLen, int) and len(lValue) != iLen:
        raise CAnyError_Message(sMsg="Value list is of invalid length '{}': {}".format(len(lValue), lValue))
    # endif

    lResult = []
    for iIdx, xValue in enumerate(lValue):
        try:
            lResult.append(ToInt(xValue, bDoRaise=True))

        except Exception as xEx:

            return _RaiseIfTrue(
                bDoRaise,
                _sMsg=f"Error converting element '{iIdx}' of list '{_sElement}' to integer. Value is: {xValue}",
                _xChildEx=xEx,
            )
        # endtry
    # endfor

    return lResult


# enddef

#######################################################################
# Cast to float
def ToFloat(_xValue, fDefault=None, bDoRaise=True):
    try:
        fResult = float(_xValue)
    except Exception as xEx:
        if isinstance(fDefault, float):
            return fDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Error converting '{_xValue}' to float.", _xChildEx=xEx)
    # endtry

    return fResult


# enddef

#######################################################################
# Cast to float
def DictElementToFloat(_dicData, _sElement, fDefault=None, bDoRaise=True):

    if fDefault is not None and not isinstance(fDefault, float):
        raise CAnyError_Message(sMsg=f"Default value is not a float: {fDefault}")
    # endif

    if not isinstance(_dicData, dict):
        if isinstance(fDefault, float):
            return fDefault
        # endif
        raise CAnyError_Message(sMsg="No dictionary given")
    # endif

    xValue = _dicData.get(_sElement)
    if xValue is None:
        if fDefault is not None:
            return fDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Element '{_sElement}' not found")
    # enddef

    try:
        fResult = ToFloat(xValue, fDefault=fDefault, bDoRaise=bDoRaise)

    except Exception as xEx:

        return _RaiseIfTrue(
            bDoRaise,
            _sMsg=f"Error converting element '{_sElement}' to float. Value is: {xValue}",
            _xChildEx=xEx,
        )
    # endtry

    return fResult


# enddef


#######################################################################
# Cast to integer
def DictElementToFloatList(_dicData, _sElement, iLen=None, lDefault=None, bDoRaise=True):

    if lDefault is not None:
        if not isinstance(lDefault, list):
            raise CAnyError_Message(sMsg=f"Default value is not a list: {lDefault}")
        elif isinstance(iLen, int) and len(lDefault) != iLen:
            raise CAnyError_Message(sMsg="Default list is of invalid length '{}': {}".format(len(lDefault), lDefault))
        # endif
    # endif

    if not isinstance(_dicData, dict):
        if isinstance(lDefault, list):
            return lDefault
        # endif
        raise CAnyError_Message(sMsg="No dictionary given")
    # endif

    lValue = _dicData.get(_sElement)
    if lValue is None:
        if isinstance(lDefault, list):
            return lDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Element '{_sElement}' not found")
    # enddef

    if not isinstance(lValue, list):
        raise CAnyError_Message(sMsg=f"Element '{_sElement}' is not a list")
    # endif

    if isinstance(iLen, int) and len(lValue) != iLen:
        raise CAnyError_Message(sMsg="Value list is of invalid length '{}': {}".format(len(lValue), lValue))
    # endif

    lResult = []
    for iIdx, xValue in enumerate(lValue):
        try:
            lResult.append(ToFloat(xValue, bDoRaise=True))

        except Exception as xEx:

            return _RaiseIfTrue(
                bDoRaise,
                _sMsg=f"Error converting element '{iIdx}' of list '{_sElement}' to float. Value is: {xValue}",
                _xChildEx=xEx,
            )
        # endtry
    # endfor

    return lResult


# enddef


#######################################################################
def ToBool(_xValue, bDefault=None, bDoRaise=True):
    try:
        if isinstance(_xValue, bool):
            bResult = _xValue

        elif isinstance(_xValue, str):
            if _xValue.lower() == "true":
                bResult = True
            elif _xValue.lower() == "false":
                bResult = False
            else:
                bResult = int(_xValue) != 0
            # endif
        else:
            bResult = int(_xValue) != 0
        # endif

    except Exception as xEx:
        if isinstance(bDefault, bool):
            return bDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Error converting '{_xValue}' to bool.", _xChildEx=xEx)
    # endtry

    return bResult


# enddef

#######################################################################
# Cast to bool
def DictElementToBool(_dicData, _sElement, bDefault=None, bDoRaise=True):

    if bDefault is not None and not isinstance(bDefault, bool):
        raise CAnyError_Message(sMsg=f"Default value is not a boolean: {bDefault}")
    # endif

    if not isinstance(_dicData, dict):
        if isinstance(bDefault, bool):
            return bDefault
        # endif
        raise CAnyError_Message(sMsg="No dictionary given")
    # endif

    xValue = _dicData.get(_sElement)
    if xValue is None:
        if bDefault is not None:
            return bDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Element '{_sElement}' not found")
    # enddef

    try:
        bResult = ToBool(xValue, bDefault=bDefault, bDoRaise=bDoRaise)

    except Exception as xEx:

        return _RaiseIfTrue(
            bDoRaise,
            _sMsg=f"Error converting element '{_sElement}' to integer. Value is: {xValue}",
            _xChildEx=xEx,
        )
    # endtry

    return bResult


# enddef


#######################################################################
# Cast to integer
def DictElementToBoolList(_dicData, _sElement, iLen=None, lDefault=None, bDoRaise=True):

    if lDefault is not None:
        if not isinstance(lDefault, list):
            raise CAnyError_Message(sMsg=f"Default value is not a list: {lDefault}")
        elif isinstance(iLen, int) and len(lDefault) != iLen:
            raise CAnyError_Message(sMsg="Default list is of invalid length '{}': {}".format(len(lDefault), lDefault))
        # endif
    # endif

    if not isinstance(_dicData, dict):
        if isinstance(lDefault, list):
            return lDefault
        # endif
        raise CAnyError_Message(sMsg="No dictionary given")
    # endif

    lValue = _dicData.get(_sElement)
    if lValue is None:
        if isinstance(lDefault, list):
            return lDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Element '{_sElement}' not found")
    # enddef

    if not isinstance(lValue, list):
        raise CAnyError_Message(sMsg=f"Element '{_sElement}' is not a list")
    # endif

    if isinstance(iLen, int) and len(lValue) != iLen:
        raise CAnyError_Message(sMsg="Value list is of invalid length '{}': {}".format(len(lValue), lValue))
    # endif

    lResult = []
    for iIdx, xValue in enumerate(lValue):
        try:
            lResult.append(ToBool(xValue, bDoRaise=True))

        except Exception as xEx:

            return _RaiseIfTrue(
                bDoRaise,
                _sMsg=f"Error converting element '{iIdx}' of list '{_sElement}' to bool. Value is: {xValue}",
                _xChildEx=xEx,
            )
        # endtry
    # endfor

    return lResult


# enddef


#######################################################################
# Cast to string
def ToString(_xValue, sDefault=None, bDoRaise=True):

    try:
        sResult = str(_xValue)
    except Exception as xEx:
        if isinstance(sDefault, str):
            return sDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Error converting '{_xValue}' to string.", _xChildEx=xEx)
    # endtry

    return sResult


# enddef

#######################################################################
# Cast to string
def DictElementToString(_dicData, _sElement, sDefault=None, bDoRaise=True):

    if sDefault is not None and not isinstance(sDefault, str):
        raise CAnyError_Message(sMsg=f"Default value is not a string: {sDefault}")
    # endif

    if not isinstance(_dicData, dict):
        if isinstance(sDefault, int):
            return sDefault
        # endif
        raise CAnyError_Message(sMsg="No dictionary given")
    # endif

    xValue = _dicData.get(_sElement)
    if xValue is None:
        if sDefault is not None:
            return sDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Element '{_sElement}' not found")
    # enddef

    try:
        sResult = ToString(xValue)

    except Exception as xEx:

        return _RaiseIfTrue(
            bDoRaise,
            _sMsg=f"Error converting element '{_sElement}' to string. Value is: {xValue}",
            _xChildEx=xEx,
        )
    # endtry

    return sResult


# enddef


#######################################################################
# Cast to integer
def DictElementToStringList(_dicData, _sElement, iLen=None, lDefault=None, bDoRaise=True):

    if lDefault is not None:
        if not isinstance(lDefault, list):
            raise CAnyError_Message(sMsg=f"Default value is not a list: {lDefault}")
        elif isinstance(iLen, int) and len(lDefault) != iLen:
            raise CAnyError_Message(sMsg="Default list is of invalid length '{}': {}".format(len(lDefault), lDefault))
        # endif
    # endif

    if not isinstance(_dicData, dict):
        if isinstance(lDefault, list):
            return lDefault
        # endif
        raise CAnyError_Message(sMsg="No dictionary given")
    # endif

    lValue = _dicData.get(_sElement)
    if lValue is None:
        if isinstance(lDefault, list):
            return lDefault
        # endif

        return _RaiseIfTrue(bDoRaise, _sMsg=f"Element '{_sElement}' not found")
    # enddef

    if not isinstance(lValue, list):
        raise CAnyError_Message(sMsg=f"Element '{_sElement}' is not a list")
    # endif

    if isinstance(iLen, int) and len(lValue) != iLen:
        raise CAnyError_Message(sMsg="Value list is of invalid length '{}': {}".format(len(lValue), lValue))
    # endif

    lResult = []
    for iIdx, xValue in enumerate(lValue):
        try:
            lResult.append(ToString(xValue, bDoRaise=True))

        except Exception as xEx:

            return _RaiseIfTrue(
                bDoRaise,
                _sMsg=f"Error converting element '{iIdx}' of list '{_sElement}' to string. Value is: {xValue}",
                _xChildEx=xEx,
            )
        # endtry
    # endfor

    return lResult


# enddef


#######################################################################
# Cast to type
def ToType(_xValue, _typeOut, _xDefault=None, bDoRaise=True):
    if not isinstance(_typeOut, type):
        if bDoRaise is True:
            raise CAnyError_Message(sMsg=f"Error type casting could not be performed with given caster:'{_typeOut!r}'.")
        else:
            return None
        # endif
    # endif typing given

    if _typeOut is int:
        return ToInt(_xValue, iDefault=_xDefault, bDoRaise=bDoRaise)
    # endif

    if _typeOut is float:
        return ToFloat(_xValue, fDefault=_xDefault, bDoRaise=bDoRaise)
    # endif

    if _typeOut is bool:
        return ToBool(_xValue, bDefault=_xDefault, bDoRaise=bDoRaise)
    # endif

    if _typeOut is str:
        return ToString(_xValue, sDefault=_xDefault, bDoRaise=bDoRaise)
    # endif

    if isinstance(_typeOut, types.GenericAlias) and isinstance(_typeOut(), list):

        if len(_typeOut.__args__) > 1 and not isinstance(_xValue, Iterable):
            return _RaiseIfTrue(
                bDoRaise,
                _sMsg=f"Error converting '{_xValue}' to <list[{_typeOut.__args__}]>. InputValue is not iterable",
            )
        # endif

        xResult = []
        if len(_typeOut.__args__) == 1 and isinstance(_xValue, Iterable):
            xType = _typeOut.__args__[0]
            for index, xValueTemp in enumerate(_xValue):
                if isinstance(_xDefault, Iterable):
                    xElementResult = ToType(xValueTemp, xType, _xDefault[index], bDoRaise=bDoRaise)
                else:
                    xElementResult = ToType(xValueTemp, xType, _xDefault, bDoRaise=bDoRaise)
                # endif
                xResult.append(xElementResult)
            # endfor
        else:
            if isinstance(_xDefault, Iterable) and len(_xDefault) != len(_typeOut.__args__):
                return _RaiseIfTrue(
                    bDoRaise,
                    _sMsg=f"Error converting '{_xValue}' to <list[{_typeOut.__args__}]>."
                    f" DefaultValue '{_xDefault}' is given, but with wrong size",
                )
            # endif

            if isinstance(_xValue, Iterable) and len(_xValue) != len(_typeOut.__args__):
                return _RaiseIfTrue(
                    bDoRaise, _sMsg=f"Wrong Size while converting '{_xValue}' to <list[{_typeOut.__args__}]>."
                )
            # endif

            for index, xType in enumerate(_typeOut.__args__):
                if isinstance(_xValue, Iterable):
                    xValueTemp = _xValue[index]
                else:
                    xValueTemp = _xValue

                if isinstance(_xDefault, Iterable):
                    xElementResult = ToType(xValueTemp, xType, _xDefault[index], bDoRaise=bDoRaise)
                else:
                    xElementResult = ToType(xValueTemp, xType, _xDefault, bDoRaise=bDoRaise)
                # endif
                xResult.append(xElementResult)
            # endfor
        # endif
    else:
        try:
            xResult = _typeOut(_xValue)
        except Exception as xEx:
            if isinstance(_xDefault, _typeOut):
                return _xDefault
            # endif

            return _RaiseIfTrue(bDoRaise, _sMsg=f"Error converting '{_xValue}' to {_typeOut!r}.", _xChildEx=xEx)
        # endtry
    # endif

    return xResult


# enddef


############################################################################################
def DictElementToAttribute(_xObject, _dicData: dict, _sElement: str, *, _bOptional=False, _bDoRaise=True):

    bDataSet: bool = False

    if not hasattr(_xObject, _sElement):
        if _bDoRaise is True:
            raise RuntimeError(f"Parameter '{_sElement}' not available")
        else:
            return False
        # endif
    # endif

    if isinstance(getattr(_xObject, _sElement), str):
        xValue = DictElementToString(_dicData, _sElement, bDoRaise=False)
    elif isinstance(getattr(_xObject, _sElement), bool):
        xValue = DictElementToBool(_dicData, _sElement, bDoRaise=False)
    elif isinstance(getattr(_xObject, _sElement), int):
        xValue = DictElementToInt(_dicData, _sElement, bDoRaise=False)
    elif isinstance(getattr(_xObject, _sElement), float):
        xValue = DictElementToFloat(_dicData, _sElement, bDoRaise=False)
    else:
        if _bDoRaise is True:
            raise RuntimeError(f"Unsupported type of parameter '{_sElement}'")
        else:
            return False
        # endif
    # endif

    if xValue is not None:
        setattr(_xObject, _sElement, xValue)
        bDataSet = True

    elif _bOptional is False:
        if _bDoRaise is True:
            raise RuntimeError(f"Element '{_sElement}' not found in source dictionary")
        # endif
    # endif

    return bDataSet


# enddef


############################################################################################
def SetAttributesFromDict(_xObject, _dicData: dict, *, _lNames=None, _bOptional=False, _bDoRaise=True):

    if _lNames is None:
        lPars = [x for x in dir(_xObject) if not x.startswith("__") and not callable(getattr(_xObject, x))]
    else:
        lPars = _lNames
    # endif

    for sPar in lPars:
        DictElementToAttribute(_xObject, _dicData, sPar, _bOptional=_bOptional, _bDoRaise=_bDoRaise)
    # endfor


# enddef
