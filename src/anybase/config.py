#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /config.py
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

import inspect
import os
import copy
from typing import Any, Iterable, Optional, Union, TypeVar
from pathlib import Path

import ison
from . import path
from . import file
from . import filepathvars
from .cls_any_error import CAnyError, CAnyError_TaskMessage, CAnyError_Message
from .cls_anycml import CAnyCML
from . import assertion


TDictValue = TypeVar("TDictValue")


####################################################################################
def ProvideReadFilepathExt(_xPathFile: Union[str, list, tuple, Path]):
    pathConfig = path.MakeNormPath(_xPathFile)
    pathConfigExt = path.ProvideReadFilepathExt(pathConfig, [".json", ".json5", ".ison"])
    if pathConfigExt is None:
        if len(pathConfig.suffix) == 0:
            sMsg = "Config file '{0}' not found at path: {1}[.json, .json5, .ison]".format(
                pathConfig.name, pathConfig.as_posix()
            )
        else:
            sMsg = "Config file '{0}' not found at path: {1}".format(pathConfig.name, pathConfig.as_posix())
        # endif
        raise CAnyError_Message(sMsg=sMsg)
    # endif

    return pathConfigExt


# enddef


####################################################################################
# Load a config file and check its validity
def Load(
    _xPathFile: Union[str, list, tuple, Path],
    *,
    sDTI: str = "/*:*.*",
    bReplacePureVars: bool = True,
    bAddPathVars: bool = False,
    bDoThrow: bool = True,
    dicCustomVars: dict = None,
) -> dict:
    try:
        pathConfig = ProvideReadFilepathExt(_xPathFile)
    except Exception as xEx:
        sMsg = str(xEx)
        if bDoThrow:
            raise CAnyError_Message(sMsg=sMsg)
        else:
            return {"bOK": False, "sMsg": sMsg, "dicCfg": None}
        # endif
    # endif

    dicCfg = file.LoadJson(pathConfig)

    dicRes = CheckConfigType(dicCfg, sDTI)
    if not dicRes.get("bOK"):
        sTask = "Invalid configuration file '{0}'".format(pathConfig.as_posix())
        sMsg = dicRes.get("sMsg")
        if bDoThrow:
            raise CAnyError_TaskMessage(sTask=sTask, sMsg=sMsg)
        else:
            sMsg = "{}: {}".format(sTask, sMsg)
            return {"bOK": False, "sMsg": sMsg, "dicCfg": None}
        # endif
    # endif

    # Replace variables in top id element if present.
    # If no 'sId' tag is present then create one with the filebasename.
    if dicCfg.get("sId") is None:
        dicCfg["sId"] = "${filebasename}"
    # endif

    # No processing of the config, just
    # add path variables to local variables of config
    dicPathVars = filepathvars.GetVarDict(pathConfig)
    if dicCustomVars is not None:
        dicPathVars.update(dicCustomVars)
    # endif

    if bReplacePureVars is True:
        xCML = CAnyCML(dicConstVars=dicPathVars)
        dicCfg = xCML.ReplacePureVars(dicCfg)
    # endif

    if bAddPathVars is True:
        ison.util.data.AddVarsToData(dicCfg, dicLocals=dicPathVars)
    # endif

    if bDoThrow:
        return dicCfg
    else:
        return {"bOK": True, "sMsg": "", "dicCfg": dicCfg}
    # endif


# enddef


####################################################################################
# Save a config file with DTI element
def Save(
    _xFilePath: Union[str, list, tuple, Path],
    _dicData: dict,
    *,
    sDTI: Optional[str] = None,
):
    dicData = copy.deepcopy(_dicData)

    # Add an empty DTI field if it does not exist
    if "sDTI" not in dicData:
        dicTemp = {"sDTI": ""}
        dicTemp.update(dicData)
        dicData = dicTemp
        # dicData.update({"sDTI": ""})
    # endif

    # if a DTI value is given in kwargs, then override
    # DTI field in dicData
    if sDTI is not None:
        dicData["sDTI"] = sDTI
    else:
        # if no DTI is given and also none is present in dicData,
        # then set type of data to "unknown:1"
        if len(dicData.get("sDTI")) == 0:
            dicData["sDTI"] = "unknown:1"
        # endif
    # endif

    pathFile = path.ProvideWriteFilepathExt(_xFilePath, ".json")

    file.SaveJson(pathFile, dicData, iIndent=4)


# enddef


####################################################################################
# Split DTI string into parts
def SplitDti(_sDTI: str):
    assertion.FuncArgTypes()

    iIdx = _sDTI.find(":")
    if iIdx < 0:
        lVerVal = [-1, -1]
        sType = _sDTI
    else:
        sType = _sDTI[0:iIdx]
        sVer = _sDTI[iIdx + 1 :]

        lVer = sVer.split(".")

        lVerVal = []
        for sVer in lVer:
            if sVer == "*":
                lVerVal.append(-1)
            else:
                lVerVal.append(int(sVer))
            # endif
        # endfor

        if len(lVerVal) == 1:
            lVerVal.append(0)
        # endif
    # endif

    if len(sType) == 0:
        raise CAnyError_Message(sMsg="No type given in DTI string: {0}".format(_sDTI))
    # endif

    # if type does not start with "/", then add "catharsys" as first type
    lType = sType.split("/")
    if len(lType[0]) == 0:
        del lType[0]
    else:
        lType.insert(0, "catharsys")
    # endif

    for sType in lType:
        if len(sType) == 0:
            raise CAnyError_Message(sMsg="Empty type element in DTI string: {0}".format(_sDTI))
        # endif
    # endfor

    return {"lVersion": lVerVal, "lType": lType}


# enddef


####################################################################################
def JoinDti(_sDti: str, *_tArgv: Iterable[str]) -> str:
    dicDti = SplitDti(_sDti)
    lType = dicDti["lType"]
    lVersion = dicDti["lVersion"]

    for sArg in _tArgv:
        if not isinstance(sArg, str):
            raise RuntimeError("Cannot join element '{}' to DTI: {}".format(sArg, _sDti))
        # endif
        lType.append(sArg)
    # endfor

    sDti = "/{}:{}".format("/".join(lType), ".".join([str(x) for x in lVersion]))
    return sDti


# enddef


####################################################################################
# Check config data type
def CheckDti(_sCfgDti: str, _sTrgDti: str) -> dict:
    assertion.FuncArgTypes()

    bOK = True
    sMsg = ""

    if not isinstance(_sCfgDti, str):
        return {"bOK": False, "sMsg": "Config DTI argument is not a string"}
    # endif

    if not isinstance(_sTrgDti, str):
        return {"bOK": False, "sMsg": "Target DTI argument is not a string"}
    # endif

    dicDTI = SplitDti(_sCfgDti)
    lCfgType = dicDTI.get("lType")
    lCfgVer = dicDTI.get("lVersion")

    dicTrgDti = SplitDti(_sTrgDti)
    lTrgType = dicTrgDti.get("lType")
    lTrgVer = dicTrgDti.get("lVersion")

    for iIdx in range(len(lTrgType)):
        if iIdx >= len(lCfgType):
            bOK = False
            sMsg = "Target type '{0}' is more specific than config type '{1}'.".format(_sTrgDti, _sCfgDti)
            break
        # endif

        if not (
            lTrgType[iIdx] == "*"
            or lTrgType[iIdx] == "?"
            or lCfgType[iIdx] == "*"
            or lCfgType[iIdx] == "?"
            or lTrgType[iIdx] == lCfgType[iIdx]
        ):
            bOK = False
            sMsg = "Target type '{0}' does not match config type '{1}'.".format(_sTrgDti, _sCfgDti)
            break
        # endif

        # If it's either type list's last element, and this element is a '*',
        # then the remainder of either list does not have to be checked
        if (iIdx + 1 == len(lTrgType) and lTrgType[iIdx] == "*") or (
            iIdx + 1 == len(lCfgType) and lCfgType[iIdx] == "*"
        ):
            break
        # endif

        if iIdx + 1 == len(lTrgType) and iIdx + 1 < len(lCfgType):
            bOK = False
            sMsg = "Config type '{0}' is more specific than target type '{1}'.".format(_sCfgDti, _sTrgDti)
            break
        # endif
    # endfor

    if bOK:
        # If major versions are not equal, than there is no match
        if not (lCfgVer[0] < 0 or lTrgVer[0] < 0 or lCfgVer[0] == lTrgVer[0]):
            bOK = False
            sMsg = "Major versions of target type '{0}' " "and config type '{1}' are incompatible".format(
                _sTrgDti, _sCfgDti
            )

        elif not (lCfgVer[1] < 0 or lTrgVer[1] < 0 or lTrgVer[1] <= lCfgVer[1]):
            bOK = False
            sMsg = "Minor versions of target type '{0}' " "and config type '{1}' are incompatible".format(
                _sTrgDti, _sCfgDti
            )
        # endif
    # endif

    return {
        "bOK": bOK,
        "sMsg": sMsg,
        "sCfgDti": _sCfgDti,
        "lCfgType": lCfgType,
        "lCfgVer": lCfgVer,
        "sTrgDti": _sTrgDti,
        "lTrgType": lTrgType,
        "lTrgVer": lTrgVer,
    }


# enddef


####################################################################################
# Check DTI
def IsDti(_sCfgDti: str, _sTrgDti: str) -> bool:
    return CheckDti(_sCfgDti, _sTrgDti)["bOK"]


# enddef


####################################################################################
# Check config data type
def CheckConfigType(_dicCfg: dict, _sTrgDti: str) -> dict:
    assertion.FuncArgTypes()

    # Get the "Data Type Info" string
    sDTI = GetDictValue(_dicCfg, "sDTI", str, sWhere=f"configuration data ({_sTrgDti})")

    return CheckDti(sDTI, _sTrgDti)


# enddef


####################################################################################
# Test for config type
def IsConfigType(_dicCfg: dict, _sTrgDti: str) -> bool:
    assertion.FuncArgTypes()

    if _dicCfg is None:
        return False
    # endif

    dicRes = CheckConfigType(_dicCfg, _sTrgDti)
    return dicRes.get("bOK") is True


# enddef


####################################################################################
# Check config data type
def AssertConfigType(_dicCfg: dict, _sTrgDti: str) -> dict:
    assertion.FuncArgTypes()

    dicResult = CheckConfigType(_dicCfg, _sTrgDti)
    if not dicResult.get("bOK"):
        raise CAnyError_Message(
            sMsg="Invalid configuration data of type '{0}' given: {1}".format(
                dicResult.get("sCfgDti"), dicResult.get("sMsg")
            )
        )
    # endif

    return dicResult


# enddef


####################################################################################
# Get all data blocks in a dictionary, that use as id a DTI which matches
# the given DTI.
def GetDataBlocksOfType(_dicData: dict, _sDti: str) -> list:
    assertion.FuncArgTypes()

    lRes = []

    for sDataDti in _dicData:
        dicR = CheckDti(sDataDti, _sDti)
        if dicR.get("bOK"):
            xData = _dicData.get(sDataDti)
            if isinstance(xData, list):
                lRes.extend(xData)
            else:
                lRes.append(xData)
            # endif
        # endif
    # endfor

    # Add local and global variables from parent dictionary
    # to selected dictionary, so that these variables are
    # available, when the element is parsed by itself.
    for xRes in lRes:
        if isinstance(xRes, dict) is True:
            ison.util.data.AddLocalGlobalVars(xRes, _dicData, bThrowOnDisallow=False)
        # endif
    # endfor

    return lRes


# enddef


# DEPRECATED: Use GetDictValue()
# ####################################################################################
# # Get dictionary at given path of nested dictionaries
# def GetElementAtPath(_dicData: dict, _sPath: str, sTypename: str="Path", bRaiseException: bool=True):
#     assertion.FuncArgTypes()

#     lPath = _sPath.split("/")

#     dicX = _dicData
#     for sX in lPath:
#         dicX = dicX.get(sX)
#         if dicX is None:
#             if bRaiseException:
#                 raise CAnyError_Message(sMsg="{0} '{1}' not found.".format(sTypename, _sPath))
#             else:
#                 break
#             # endif
#         # endif
#     # endfor

#     return dicX
# # enddef


####################################################################################
# Get dictionary at given path of nested dictionaries
def SetElementAtPath(_dicData: dict, _sPath: str, _xEl: Any):
    assertion.FuncArgTypes()

    lPath = _sPath.split("/")

    dicX = _dicData
    for iIdx in range(0, len(lPath)):
        sX = lPath[iIdx]
        dicY = dicX.get(sX)
        if dicY is None:
            if iIdx < len(lPath) - 1:
                dicX[sX] = {}
                dicX = dicX[sX]
            else:
                dicX[sX] = _xEl
                break
            # endif
        else:
            if iIdx == len(lPath) - 1:
                dicX[sX] = _xEl
                break
            else:
                dicX = dicY
            # endif
        # endif
    # endfor


# enddef


######################################################################################
def GetDictPaths(_dicX: dict, sDTI: Optional[str] = None) -> list:
    assertion.FuncArgTypes()

    lPaths = []
    for sEl in _dicX:
        dicSub = _dicX.get(sEl)
        if isinstance(dicSub, dict):
            if "sDTI" not in dicSub:
                lSubPaths = GetDictPaths(dicSub, sDTI=sDTI)
                lPaths.extend(["{0}/{1}".format(sEl, x) for x in lSubPaths])

            elif isinstance(sDTI, str):
                dicR = CheckDti(dicSub.get("sDTI"), sDTI)
                if dicR.get("bOK"):
                    lPaths.append(sEl)
                # endif

            else:
                lPaths.append(sEl)
            # endif
        # endif is dict
    # endfor

    return lPaths


# enddef


######################################################################################
def GetDictValue(
    _dicX: dict,
    _sKey: str,
    _typX: TDictValue,
    *,
    xDefault: Optional[TDictValue] = None,
    sWhere: str = "dictionary",
    sMsgNotFound=None,
    sMsgWrongType=None,
    bOptional: bool = False,
    bAllowKeyPath: bool = False,
    bIsDtiKey: bool = False,
) -> TDictValue:
    assertion.FuncArgTypes()

    if xDefault is not None:
        if not isinstance(xDefault, _typX):
            raise CAnyError_Message(sMsg="Default value is not of type '{}'".format(_typX.__name__))
        # endif
    # endif

    xValue = None

    # If the key is a DTI string, then look for a compatible DTI key
    # in the dictionary _dicX.
    if bIsDtiKey is True:
        sSrcKey = None
        for sDicKey in _dicX:
            dicRes = CheckDti(sDicKey, _sKey)
            if dicRes["bOK"] is True:
                sSrcKey = sDicKey
                break
            # endif
        # endfor

        if sSrcKey is not None:
            xValue = _dicX[sSrcKey]
        # endif

    else:
        # The given key is not a DTI string
        xValue = _dicX.get(_sKey)

        if xValue is None and bAllowKeyPath is True:
            # Try interpreting key as path
            bFoundValue = True
            lKey: list[str] = _sKey.split("/")
            dicY = _dicX
            for sPartKey in lKey:
                if not isinstance(dicY, dict):
                    bFoundValue = False
                    break
                # endif
                dicY = dicY.get(sPartKey)
                if dicY is None:
                    bFoundValue = False
                    break
                # endif
            # endfor partial keys

            if bFoundValue is True:
                xValue = dicY
            # endif
        # endif
    # endif

    if xValue is None:
        xValue = xDefault
    # endif

    if xValue is None:
        if bOptional is False:
            if sMsgNotFound is None:
                sMsg = "Element '{sKey}' not found in {sWhere}".format(sKey=_sKey, sWhere=sWhere)
            else:
                sMsg = sMsgNotFound.format(sKey=_sKey, sWhere=sWhere)
            # endif
            raise CAnyError_Message(sMsg=sMsg)
        else:
            return None
        # endif
    # endif

    if not isinstance(xValue, _typX):
        if _typX is float and isinstance(xValue, int):
            xValue = float(xValue)
        else:
            if sMsgWrongType is None:
                sMsg = "Element '{sKey}' is of type '{sValType}' but should be of type '{sTrgType}' in {sWhere}".format(
                    sKey=_sKey,
                    sValType=type(xValue).__name__,
                    sTrgType=_typX.__name__,
                    sWhere=sWhere,
                )
            else:
                sMsg = sMsgWrongType.format(
                    sKey=_sKey,
                    sValType=type(xValue).__name__,
                    sTrgType=_typX.__name__,
                    sWhere=sWhere,
                )
            # endif
            raise CAnyError_Message(sMsg=sMsg)
        # endif
    # endif

    return xValue


# enddef


######################################################################################
def StoreDictValuesInObject(
    _objTrg,
    _dicSrc: dict,
    _lMap: Iterable,
    sTrgAttributePrefix: str = None,
    sWhere: str = "dictionary",
    sMsgNotFound=None,
    sMsgWrongType=None,
):
    assertion.FuncArgTypes()

    for tMap in _lMap:
        if len(tMap) < 2:
            raise CAnyError_Message(sMsg="Invalid dictionary element map: {}".format(str(tMap)))
        # endif

        sTrgKey = tMap[0]
        iNextIdx = 1
        if isinstance(tMap[iNextIdx], str):
            sSrcKey = tMap[iNextIdx]
            iNextIdx = 2
        elif isinstance(tMap[iNextIdx], type):
            sSrcKey = sTrgKey
            iNextIdx = 1
        else:
            raise CAnyError_Message(sMsg="Invalid type of second element in tuple: {}".format(str(tMap)))
        # endif

        if sTrgAttributePrefix is not None:
            sTrgKey = sTrgAttributePrefix + sTrgKey
        # endif

        typValue = tMap[iNextIdx]
        if not isinstance(typValue, type):
            raise CAnyError_Message(sMsg="Invalid type of element {} in tuple: {}".format(iNextIdx + 1, str(tMap)))
        # endif
        iNextIdx += 1

        if len(tMap) >= iNextIdx + 1:
            xDefault = tMap[iNextIdx]
        else:
            xDefault = None
        # endif
        iNextIdx += 1

        if len(tMap) >= iNextIdx + 1:
            bOptional = tMap[iNextIdx]
        else:
            bOptional = False
        # endif

        if not hasattr(_objTrg, sTrgKey):
            raise CAnyError_Message(sMsg="Target object does not have attribute '{}'".format(sTrgKey))
        # endif

        xValue = GetDictValue(
            _dicSrc,
            sSrcKey,
            typValue,
            xDefault=xDefault,
            bOptional=bOptional,
            sWhere=sWhere,
            sMsgNotFound=sMsgNotFound,
            sMsgWrongType=sMsgWrongType,
        )

        setattr(_objTrg, sTrgKey, xValue)

    # endfor


# enddef
