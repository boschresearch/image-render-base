#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \CheckFuncTypes.py
# Created Date: Wednesday, May 25th 2022, 11:51:33 am
# Author: RB - Dirk Raproeger
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

import dataclasses
import types

from collections.abc import Iterable

from anybase.cls_any_error import CAnyError_Message
from anybase import config
from anybase import convert

from catharsys.decs.decorator_log import logFunctionCall


class CDeprecatedField:
    """is a qualifier for annotations in ParamClasses.
    Parameter, that are optional and can be filled automatically with defaults
    can be handled with this Field. lVector = [1,2,3] will not be aceptable,
    because mutable defaults are errorness
    """

    def __init__(self, arg=None) -> None:

        if isinstance(arg, str):  # single string
            self.lDeprecated = [arg]
        elif isinstance(arg, list):  # list of strings
            self.lDeprecated = []
            for sArg in arg:
                if isinstance(arg, str):
                    self.lDeprecated.append(sArg)
                else:
                    raise CAnyError_Message(sMsg="Deprecated field must contain a string or a list of strings")
                # endif
            # endfor
        else:
            raise CAnyError_Message(sMsg="Deprecated field must contain a string or a list of strings")
        # endif

    # end def


# end class


class CDefaultField:
    """is a qualifier for annotations in ParamClasses.
    Parameter, that are optional and can be filled automatically with defaults
    can be handled with this Field. lVector = [1,2,3] will not be aceptable,
    because mutable defaults are errorness
    """

    def __init__(self, arg=None) -> None:
        self.xDefault = arg

    # enddef


# endclass

# end def


# end class


class CDisplayField:
    """is a qualifier for annotations in ParamClasses.
    Parameter, that are used in GUIs may contain a display Name for better
    acceptance
    """

    def __init__(self, arg: str = None) -> None:
        if not isinstance(arg, str):
            raise TypeError("displaying alternative texts must be iniitalized with strings")
        # endif
        self.sDIsplay = arg

    # end def

    # end def


# end class


class CRequiredField:
    """is a qualifier for annotations in ParamClasses.
    Parameter, that are required can be marked,
    and if some attributes in typechecking is required also,
    this can be done by giving the class types that are expected"""

    def __init__(
        self,
        _xArg=None,
        _tArgOptional=None,
    ) -> None:
        self.xTypeCheckingArg = _xArg
        self.txOptionalChecks = _tArgOptional if isinstance(_tArgOptional, (tuple, list)) else (_tArgOptional,)

    # enddef


# endclass

# end def


# end class


class COptionField:
    """is a qualifier for annotations in ParamClasses.
    Parameter, that are required can be marked,
    and if some attributes in typechecking is required also,
    this can be done by giving the class types that are expected

    Usage:
        sMode: str = CParamFields.OPTIONS(["INIT", "FRAME_UPDATE"], xDefault="INIT")

    """

    def __init__(self, arg=None, xDefault=None) -> None:
        self.xTypeOptionArg = arg
        self.xDefaultOption = xDefault

        if xDefault is not None and xDefault not in arg:
            raise CAnyError_Message(sMsg=f"defaultOption {xDefault} is not in Options({arg})")
        # endif

    # enddef


# endclass


# end class


class CHintField:
    """is a qualifier for annotations in ParamClasses.
    Parameter, that are required can be marked,
    and if some attributes in typechecking is required also,
    this can be done by giving the class types that are expected"""

    def __init__(self, sHint: str) -> None:
        self.sHint = sHint

    # enddef


# endclass

# end def


# end class


def __checkAnnotations(cls, _dicClsAnnotations):
    # Do we have any Field members that don't also have annotations?
    # --- these names are adressed already with 'startswith'
    #           "__module__", "__annotations__", "__dict__", "__weakref__", "__doc__"
    lsSpecialNames = list()

    for sName, xValue in cls.__dict__.items():
        if sName.startswith("__") or sName in lsSpecialNames or callable(xValue):
            continue
        # enf if

        if sName not in _dicClsAnnotations:
            raise TypeError(f"'{sName!r}' of <{cls}> is a field but has no type annotation")
        # enf if
    # end for


# end def


def _ProcessParamClass(cls):
    """this wrapper is similiar to dataclasses implementation of the python lib"""
    # Now that dicts retain insertion order, there's no reason to use
    # an ordered dict.  I am leveraging that ordering here, because
    # derived class fields overwrite base class fields, but the order
    # is defined by the base class, which is found first.
    dicFields = {}

    dicClsAnnotations = cls.__dict__.get("__annotations__", {})
    __checkAnnotations(cls, dicClsAnnotations)

    # Now find fields in our class.  While doing so, validate some
    # things, and set the default values (as class attributes) where
    # we can.
    lClsFields = [
        (
            dataclasses._get_field(cls, a_name=sName, a_type=xType, default_kw_only=None),
            dataclasses._get_field(cls, a_name=f"__{sName}_default", a_type=xType, default_kw_only=None),
        )
        for sName, xType in dicClsAnnotations.items()
        if not sName.startswith("sDisplay_")
    ]

    lClsDisplayFields = [
        dataclasses._get_field(cls, a_name=sName, a_type=xType, default_kw_only=None)
        for sName, xType in dicClsAnnotations.items()
        if sName.startswith("sDisplay_")
    ]

    for xField in lClsDisplayFields:
        if xField.default is not None:
            raise TypeError(
                f"'{xField.name}' of <{cls}> is a sDisplay-field for code completion, that must be given with default None"
            )
        # endif

        if not xField.name[9:] in dicClsAnnotations:
            raise ValueError(
                f"'{xField.name}' declares an alternative text, but the base field '{xField.name[9:]}' doesn't exist in <{cls}>"
            )
        # endif
    # endfor

    idName = 0
    idDefault = 1
    for tupleField in lClsFields:
        tupleField[idDefault].default = tupleField[idName].default
    # endfor default copy

    for tupleField in lClsFields:
        sName = tupleField[idName].name
        sNameDefault = tupleField[idDefault].name

        dicFields[sNameDefault] = tupleField[idDefault]
        dicFields[sName] = tupleField[idName]
        dicFields[sName].default = sName

        # #---- MISSING -------
        if isinstance(dicFields[sNameDefault].default, type(dataclasses.MISSING)):
            raise TypeError(
                f"'{sName!r}' of <{cls}> is a field with annotation but no DEFAULT, HINT or other paramFields were given"
            )
        # endif

        # in normal case there is given more than one qualifier for each element
        if not isinstance(dicFields[sNameDefault].default, tuple):
            dicFields[sNameDefault].default = (dicFields[sNameDefault].default,)
        # endif

        setTupleIds = set(id for id in range(len(dicFields[sNameDefault].default)))

        iValidDefaultFieldCnt = 0
        # #---- handle (optional) HINT ----
        for id, xHint in enumerate(dicFields[sNameDefault].default):
            if isinstance(xHint, CHintField):
                setattr(cls, f"{sName}_hint", xHint.sHint)
                setTupleIds.remove(id)
                break
            # endif check instance
        # endfor hint

        # #---- handle (optional) DEPRECATED ----
        for id, xDeprecated in enumerate(dicFields[sNameDefault].default):
            if isinstance(xDeprecated, CDeprecatedField):
                setattr(cls, f"{sName}_deprecatedNames", xDeprecated.lDeprecated)
                setTupleIds.remove(id)
                break
            # endif check instance
        # endfor hint

        # #---- handle (optional) DISPLAY ----
        for id, xDisplay in enumerate(dicFields[sNameDefault].default):
            if isinstance(xDisplay, CDisplayField):
                setattr(cls, f"sDisplay_{sName}", xDisplay.sDIsplay)
                setTupleIds.remove(id)
                break
            # endif check instance
        # endfor display

        # #---- handle (optional) REQUIRED ----
        iRequiredFound = -1
        for id, xRequired in enumerate(dicFields[sNameDefault].default):
            if isinstance(xRequired, CRequiredField):
                iRequiredFound = id
                iValidDefaultFieldCnt += 1
                lAllTypes = list(xRequired.txOptionalChecks)
                lAllTypes.append(xRequired.xTypeCheckingArg)

                lbWrongListDeclaration = [isinstance(xType, (list, tuple)) for xType in lAllTypes]
                # wrong declaration: CParamFields.REQUIRED([float, float, float])
                if any(lbWrongListDeclaration):
                    raise TypeError(
                        f"'{sName!r}' of <{cls}> has wrong REQUIRED declaration"
                        " (probably list[type1,type2...] is the correct one"
                    )
                # endif

                lbGenericRequiredType = [isinstance(xType, types.GenericAlias) for xType in lAllTypes]

                # if annotation is types.Generic no other type check should it be
                if any(lbGenericRequiredType) and isinstance(dicFields[sName].type, types.GenericAlias):
                    raise TypeError(
                        f"'{sName!r}' of <{cls}> is a field with annotation of {dicFields[sName].type} and the"
                        " RequiredField also contains a genericAlias, this is not allowed, please drop one of that"
                    )
                # endif

                # if main type check is generic alias, the annotation should be list or tuple
                if (
                    isinstance(xRequired.xTypeCheckingArg, types.GenericAlias)
                    and dicFields[sName].type is not list
                    and dicFields[sName].type is not tuple
                ):
                    raise TypeError(
                        f"'{sName!r}' of <{cls}> is a field with annotation of {dicFields[sName].type} but the"
                        " main RequiredField contains a genericAlias as type check, this is not allowed"
                    )
                # endif

                setTupleIds.remove(id)
                break
            # endif check instance
        # endfor required

        # #---- handle (optional) OPTION ----
        iOptionFound = -1
        for id, xOption in enumerate(dicFields[sNameDefault].default):
            if isinstance(xOption, COptionField):
                iOptionFound = id
                iValidDefaultFieldCnt += 1
                setattr(cls, f"{sName}_options", xOption.xTypeOptionArg)
                setTupleIds.remove(id)
                break
            # endif check instance
        # endfor option

        # #---- handle (optional) DEFAULT ----
        iDefaultFound = -1
        for id, xOption in enumerate(dicFields[sNameDefault].default):
            if isinstance(xOption, CDefaultField):
                iDefaultFound = id
                iValidDefaultFieldCnt += 1

                # test type casting, it throws an exception internally when it fails
                xOption.xDefault = convert.ToType(xOption.xDefault, dicFields[sName].type)

                setTupleIds.remove(id)
                break
            # endif check instance
        # endfor option

        if iValidDefaultFieldCnt == 0:
            raise TypeError(f"'{sName!r}' of <{cls}> has no field of (REQUIRED,DEFAULT,OPTION)!!")
        # endif

        if iValidDefaultFieldCnt > 1:
            raise TypeError(f"'{sName!r}' of <{cls}> only one field of (REQUIRED,DEFAULT,OPTION) is allowed!!")
        # endif

        dicFields[sNameDefault].default = dicFields[sNameDefault].default[
            max(iDefaultFound, iRequiredFound, iOptionFound)
        ]

        # all other Fields should be handled, so only the default value is left
        if len(setTupleIds) > 0:
            sUnhandledFields = "("
            for index in setTupleIds:
                sUnhandledFields += f"{type(dicFields[sNameDefault].default[index])},"
            # endfor

            raise TypeError(
                f"'{sName!r}' of <{cls}> has some unhandled fields {sUnhandledFields},"
                " implementation of _ProcessParamClass() is incomplete!!"
            )
        # endif

        # #---- the important attributes are generated ----------
        # setattr(cls, sNameDefault, tupleField[idDefault].default)
        setattr(cls, sName, sName)
    # endfor

    # endfor all clsFields

    # Remember all of the fields on our class (including bases).  This
    # also marks this class as being a dataclass.
    setattr(cls, dataclasses._FIELDS, dicFields)

    # the c'tor (__init__) will be build automatically, therefore, the code is given as list line per line
    dataclasses._set_new_attribute(
        cls,
        "__init__",
        dataclasses._create_fn(
            name="__init__",
            args=("self", "_dictArgs", "_sAdditionalErrorMsg=None"),
            body=[
                # capsulate messaging to be able to call in exception but also in printing deprecated warnings
                "def _getDefaultMsg():",
                " if isinstance( _sAdditionalErrorMsg, str ):",
                "  sDefaultMsg = '\\n  ' + _sAdditionalErrorMsg + '\\n  ' + _DefaultErrorMsg( _dictArgs )",
                " else:",
                "  sDefaultMsg = '\\n  ' + _DefaultErrorMsg( _dictArgs )",
                " return sDefaultMsg",
                "self._sDefaultMsg = _getDefaultMsg()",
                # body of ctor, try init and build param object, raises exceptions for failure
                "try:",
                ' lField_defaults = [xField for xField in fields(self) if xField.name.endswith("_default")]',
                ' lField_names = [xField.name for xField in fields(self) if not xField.name.endswith("_default")]',
                # handle (store) the xxx_default fields
                # in addition to specified names, default values are stored also inside the instance
                " for xDefaultField in lField_defaults:",
                "  self.__setattr__(xDefaultField.name[2:-8], xDefaultField.default)",
                # go through all given dict items and pick the relevant for that class
                " for sName, xValue in _dictArgs.items():",
                "  if sName in lField_names:",
                #   automatically type cast to annotated type
                "   xValueCasted = ConvertTypeCast(xValue, lField_defaults[lField_names.index(sName)].type)",
                #   instance get its own attribute, that what in class declaration specified
                "   self.__setattr__(sName, xValueCasted)",
                # for those values, which are not given, the default values are used
                " for xDefaultField in lField_defaults:",
                "  sName = xDefaultField.name[2:-8]",
                "  xValue = getattr(self, sName)",
                "  xValue = _handleDefault(cls, self, _dictArgs, sName, xValue, xDefaultField.default)",
                "  self.__setattr__(sName, xValue)",
                # bool check with integer representation
                " lField_names_bool = [sName for sName in lField_names if sName.startswith('b')]",
                " for sBoolName in lField_names_bool:",
                "  sIntegerBoolName = 'i' + sBoolName[1:]",
                "  if sIntegerBoolName in _dictArgs:",
                "   if sIntegerBoolName in lField_names:",
                #    raise an exception when both varnames for bool AND integer exists
                "    raise CAnyError_Message(sMsg=f'ParameterField <{sIntegerBoolName}> AND <{sBoolName}> exists')",
                "   if sBoolName in _dictArgs:",
                "    raise CAnyError_Message(sMsg=f'dictionary contains both <{sIntegerBoolName}> AND <{sBoolName}>')",
                # end if
                "   iBoolCasted = ConvertTypeCast(_dictArgs[sIntegerBoolName], int)",
                "   self.__setattr__(sBoolName, iBoolCasted > 0)",
                #   signalize a warning
                "   sMsg = f'please adapt the configuration for transferring a dict{self._sDefaultMsg}'",
                "   sMsg += f'\\nbuilding a boolean <{sBoolName}> from integer <{sIntegerBoolName}> is deprecated'",
                "   printLog(sMsg)",
                "   print(sMsg)",
                # build the exception msg
                "except Exception as xEx:",
                # raise an exception with children when anything was wrong
                ' raise CAnyError_Message( sMsg=f"transferring a dict {self._sDefaultMsg}\\n>> raises Exception !!<<", xChildEx=xEx )',
                "try:",
                " if hasattr(self, '__post_init__'):",
                "  self.__post_init__(_dictArgs)",
                "except Exception as xEx:",
                ' sMsg = f"{self.__class__.__name__} raised an exception when trying to call the __post_init__ constructor"',
                " raise CAnyError_Message(sMsg=sMsg, xChildEx=xEx)",
            ],
            locals={
                "_handleDefault": _handleDefault,
                "_DefaultErrorMsg": _DefaultErrorMsg,
                "ConvertTypeCast": convert.ToType,
                "fields": dataclasses.fields,
                "printLog": logFunctionCall.PrintLog,
                "cls": cls,
            },
            globals={"CAnyError_Message": CAnyError_Message},
        ),
    )

    return cls


# enddef


def IfNone(_inCheck, _ifNone):
    """in automatic distionary transfer into parameter, some nones can be afterwards set by new values"""
    bCheck = _inCheck is None
    return (bCheck, _ifNone if bCheck else _inCheck)


# enddef


# end def


def paramclass(cls=None):
    """
    this wrapper is similiar to dataclasses implementation of the python lib

    Returns the same class as was passed in, with dunder initialisation method
    added based on the fields defined in the class.

    the init method is defined as __init__( self, dictArgs )

    Usage:
        @paramclass
        class CParam:
            sDTI: str = None        !! annotations are mandatory for param fields
            xModule: str = None     !! = None, this is the Default-Value
            sUnit: str = "rad"      !! = "rad" may be a another default-value
            sVeryImportant: str = paramclass.REQUIRED() !! signalizes the init that this parameter is mandatory inside the given dictionary
            xRotAxis: list = paramclass.REQUIRED([int, float, str])

    -> initializes the class fields first with the default values, and then if they exists with given dict values (any kind that is python supported)
    -> additional dict keys are ignored
    -> if there are some missing dictArgs, the default values in class declaration is used
        : paramclass.REQUIRED() -> runs into an exception when key is not inside dictArgs
        : paramclass.REQUIRED( [int,float, string]) -> a list with (exact) 3 Elments is required. If input types are different, an automatic conversion will be done.
            -> raises an exception, if the length differs
            -> raises an exception, if conversion (if necessary) fails for an entry

        @paramclass
        class CParam:
            [optional c'tor after automatic decorated]
            def __post_init__(self, _dictArgs):
                print("following the __post_init__ pattern of dataclass:")
                print("after the default c'tor, an individual initialisation may be necessary")
    """

    def Wrap(cls):
        return _ProcessParamClass(cls)

    # enddef

    # end def wrapper

    # See if we're being called as @paramclass or @paramclass().
    if cls is None:
        # We're called with parens.
        return Wrap
    # endif

    # We're called as @paramclass without parens.
    return Wrap(cls)


# enddef


# end def


# unfortunatly, these additional attributes to the decorator function are ignored b code completion
# writing a decorator class seems to be a valid alternative, but doesn't work
# class attributes can not be set with class decorator, because thy return an object to the decorating class instead of a new class declaration
paramclass.DEFAULT = CDefaultField
paramclass.REQUIRED = CRequiredField
paramclass.OPTIONS = COptionField
paramclass.HINT = CHintField
paramclass.DISPLAY = CDisplayField
paramclass.IfNone = IfNone


class CParamFields:
    DEFAULT = CDefaultField
    DEPRECATED = CDeprecatedField
    REQUIRED = CRequiredField
    OPTIONS = COptionField
    HINT = CHintField
    DISPLAY = CDisplayField
    IfNone = IfNone


# endclass


# end class

# .....................................................................................................
# .....................................................................................................


def _DefaultErrorMsg(_dictParams: dict):
    """params may be created in many ways, the dictionary, that is investigated to build the dedicated parameter object.
    In case a json file is the base, and it was generated by catharsys envirioment, a dicVars and for more specialisation
    inside, the 'locals' are given to get the 'filepath' can be extracted
    """
    sDTI = _dictParams.get("sDTI")
    sObjectHelper = "the dict is given without a stdandard sDTI"
    if isinstance(sDTI, str):
        sObjectHelper = f"the dict refers to sDTI:'{sDTI}'"
    # endif

    sErrorMessage = f"{sObjectHelper} (detailed origin can't be evaluated, e.g. filepath can't be found)"

    if isinstance(_dictParams, dict):
        # may you are in catharsys env, try to get locals for original file
        dicLocals = _dictParams.get("__locals__")
        if isinstance(dicLocals, dict) and dicLocals.get("filepath") is not None:
            # try to get filepath for better error-message if any
            sErrorMessage = f"{sObjectHelper}\nis potentially loaded from <{dicLocals.get( 'filepath')}>"
        # endif locals are present
    # endif _dictParams is present

    return sErrorMessage


# end def

# .....................................................................................................
# .....................................................................................................


# def CreateParam(cls, _dictParams, _kwargs=None):
#     """params may be created in many ways, the dictionary, that is investigated to build the dedicated parameter object.
#     In case a json file is the base, and it was generated by catharsys envirioment, a dicVars and for more specialisation
#     inside, the 'locals' are given to get the 'filepath' can be extracted
#     """
#     sDTI = _dictParams.get("sDTI")
#     sObjectHelper = "the dict is given without a stdandard sDTI"
#     if isinstance(sDTI, str):
#         sObjectHelper = f"the dict refers to sDTI:'{sDTI}'"
#     # endif

#     sErrorMessage = f"{sObjectHelper} (detailed origin can't be evaluated, e.g. filepath can't be found)"

#     dicVars = _kwargs.get("dicVars")
#     if _kwargs is not None:
#         if isinstance(dicVars, dict):
#             # may you are in catharsys env, try to get locals for original file
#             dicLocals = dicVars.get("locals")
#             if isinstance(dicLocals, dict) and dicLocals.get("filepath") is not None:
#                 # try to get filepath for better error-message if any
#                 sErrorMessage = f"{sObjectHelper}\nis potentially loaded from <{dicLocals.get( 'filepath')}>"
#             # endif locals are present
#         # endif dictVars is present
#     # endif _kwargs is given

#     return cls(_dictParams, sErrorMessage)


# # end def


def _handleDefault(cls, _self, _dictArgs, _sFieldName: str, _xValue, _xValueDefault):

    if isinstance(_xValueDefault, CRequiredField) and isinstance(_xValue, CRequiredField):
        if hasattr(cls, _sFieldName + "_deprecatedNames"):
            lsDeprecatedNames = getattr(cls, _sFieldName + "_deprecatedNames")
            for sDepName in lsDeprecatedNames:
                xValue = _dictArgs.get(sDepName)
                if xValue is not None:
                    sMsg = "please adapt the configuration for transferring a dic,\n"
                    sMsg += f"used old and deprecated Name '{sDepName}' instead of preferred '{_sFieldName}'\n"
                    sMsg += f"{_DefaultErrorMsg( _dictArgs )}"
                    logFunctionCall.PrintLog(sMsg)
                    print(sMsg)

                    sDepName = sDepName + f"[{_sFieldName}]"
                    _xValue = _handleDefault(cls, _self, _dictArgs, sDepName, xValue, _xValueDefault)
                    return _xValue
                # end if (deprecated found)
            # end for deprecated Names
        # end if check deprecated
        # endif

        raise CAnyError_Message(sMsg=f"ParameterField({_sFieldName}) of <{cls}> is required but was not given by dict")
    # endif

    if isinstance(_xValue, CDefaultField):
        _xValue = type(_xValue.xDefault)(_xValue.xDefault)
    # endif

    # if isinstance(_xValueDefault, CRequiredField) and _xValueDefault.xTypeCheckingArg is not None:
    #     # do some checks

    #     # str checking
    #     if isinstance(_xValueDefault.xTypeCheckingArg, str):
    #         # handle sDTI and its deprecated version
    #         if _sFieldName == "sDTI" or "[sDTI]" in _sFieldName:
    #             dicCheck = config.CheckDti(_xValueDefault.xTypeCheckingArg, _xValue)
    #             if not dicCheck["bOK"]:
    #                 sCheckMsg = dicCheck["sMsg"]
    #                 raise CAnyError_Message(
    #                     sMsg=f"sDTI given ({_xValue}) doesn't fulfill the target sDTI-Reqs '{_xValueDefault.xTypeCheckingArg}'"
    #                     f"\nchecking-msg: '{sCheckMsg}'"
    #                 )
    #             # endif check fails
    #         elif _xValue != _xValueDefault.xTypeCheckingArg:
    #             raise CAnyError_Message(
    #                 sMsg=f"ParameterField({_sFieldName}) of <{cls}> is required as label as "
    #                 f"'{_xValueDefault.xTypeCheckingArg}' But it was given '{_xValue}'"
    #             )
    #         # endif str / sDTI checking
    #     # endif str checking

    #     # List checking
    #     if isinstance(_xValueDefault.xTypeCheckingArg, list):
    #         if not isinstance(_xValue, list):
    #             try:
    #                 _xValue = list(_xValue)
    #             except Exception:
    #                 raise CAnyError_Message(
    #                     sMsg=f"ParameterField({_sFieldName}) of <{cls}> is required but as list,"
    #                     " but was not given, and cannot be converted automatically"
    #                 )
    #             # end try
    #         # endif

    #         if len(_xValueDefault.xTypeCheckingArg) != len(_xValue):
    #             raise CAnyError_Message(
    #                 sMsg=f"ParameterField({_sFieldName}) of <{cls}> was given as list({len(_xValue)}),"
    #                 f" but requires dimension ({len(_xValueDefault.xTypeCheckingArg)})"
    #             )
    #         # endif

    #         for iIndex in range(0, len(_xValueDefault.xTypeCheckingArg)):
    #             try:
    #                 _xValue[iIndex] = _xValueDefault.xTypeCheckingArg[iIndex](_xValue[iIndex])
    #             except Exception:
    #                 raise CAnyError_Message(
    #                     sMsg=f"ParameterField({_sFieldName}) of <{cls}> was given, but in field[{iIndex}] the types are not compatible"
    #                     f"{type(_xValue[iIndex])} cannot be converted into required type {_xValueDefault.xTypeCheckingArg[iIndex]}"
    #                 )
    #             # end try
    #         # end for

    #     # endif list checking
    # # endif some checks for required field

    if isinstance(_xValueDefault, CRequiredField) and _xValueDefault.xTypeCheckingArg is not None:

        def _CheckHandler(_xTypeChecker, _xValue) -> str:
            bPerformConversionCheck = True

            # str checking (due to interfacing the isinstance can not be applied)
            # str is given as unconditioned type requirement
            if _xTypeChecker is str:
                bPerformConversionCheck = False
                # handle sDTI and its deprecated version
                if _sFieldName == "sDTI" or "[sDTI]" in _sFieldName:
                    sReturnMsg = f"sDTI as required, but without mandatory 'action-definition-ID-string'"
                    return (sReturnMsg, _xValue)
                    # endif check fails
                elif not isinstance(_xValue, str):
                    sReturnMsg = f"ParameterField({_sFieldName}) of <{cls}> is required as label(string)"
                    sReturnMsg += f"But it was given '{_xValue}' as <{type(_xValue)}>"
                    return (sReturnMsg, _xValue)
                # endif str / sDTI checking
            # endif str-type checking

            if isinstance(_xTypeChecker, str):
                bPerformConversionCheck = False
                # handle sDTI and its deprecated version
                if _sFieldName == "sDTI" or "[sDTI]" in _sFieldName:
                    dicCheck = config.CheckDti(_xTypeChecker, _xValue)
                    if not dicCheck["bOK"]:
                        sCheckMsg = dicCheck["sMsg"]
                        sReturnMsg = f"sDTI given ({_xValue}) doesn't fulfill the target sDTI-Reqs '{_xTypeChecker}'"
                        sReturnMsg += f"\nchecking-msg: '{sCheckMsg}'"
                        return (sReturnMsg, _xValue)

                    # endif check fails
                elif _xValue != _xTypeChecker:
                    sReturnMsg = f"ParameterField({_sFieldName}) of <{cls}> is required as label as "
                    sReturnMsg += f"'{_xTypeChecker}' But it was given '{_xValue}'"
                    return (sReturnMsg, _xValue)
                # endif str / sDTI checking
            # endif str-value checking

            # List checking
            # due to interfacing the type it is converted by python from list into GenericAlias
            if isinstance(_xTypeChecker, types.GenericAlias) and isinstance(_xTypeChecker(), list):
                bPerformConversionCheck = False
                if not isinstance(_xValue, list):
                    try:
                        _xValue = list(_xValue)
                    except Exception:
                        sReturnMsg = f"ParameterField({_sFieldName}) of <{cls}> is required but as list,"
                        sReturnMsg += " but was not given, and cannot be converted automatically"
                        return (sReturnMsg, _xValue)
                    # end try
                # endif

                iRequiredListLength = len(_xTypeChecker.__args__)
                if iRequiredListLength != len(_xValue):
                    sReturnMsg = f"ParameterField({_sFieldName}) of <{cls}> was given as list({len(_xValue)}),"
                    sReturnMsg += f" but requires dimension ({iRequiredListLength})"
                    return (sReturnMsg, _xValue)
                # endif

                for iIndex in range(0, iRequiredListLength):
                    try:
                        _xValue[iIndex] = _xTypeChecker.__args__[iIndex](_xValue[iIndex])
                    except Exception:
                        sReturnMsg = f"ParameterField({_sFieldName}) of <{cls}> was given, but in field[{iIndex}] the types are not compatible"
                        sReturnMsg += (
                            f"{type(_xValue[iIndex])} cannot be converted into required type {_xTypeChecker[iIndex]}"
                        )
                        return (sReturnMsg, _xValue)
                    # end try
                # end for
            # endif list checking

            # conversion into desired type?
            if bPerformConversionCheck:
                try:
                    # reduce if necessary to integral type
                    if isinstance(_xValue, Iterable):
                        _xValue = _xValue[0]
                    # endif

                    _xValue = convert.ToType(_xValue, _xTypeChecker)
                except Exception:
                    sReturnMsg = f"ParameterField({_sFieldName}) of <{cls}> was given, but the type is not compatible"
                    sReturnMsg += f"{type(_xValue)} cannot be converted into required type {_xTypeChecker}"
                    return (sReturnMsg, _xValue)
                # end try
            # endif 'normal' conversion checking

            return (None, _xValue)

        # enddef inner check Handler

        # check first arg
        sMsg, _xValue = _CheckHandler(_xValueDefault.xTypeCheckingArg, _xValue)
        if sMsg is not None:
            # try optional ones, if given
            lxOptionalTypeChecking = [xChecker for xChecker in _xValueDefault.txOptionalChecks if xChecker is not None]
            for xChecker in lxOptionalTypeChecking:
                sOptionalMsg, _xValue = _CheckHandler(xChecker, _xValue)
                if sOptionalMsg is None:
                    sMsg = None
                    break
                # endif
                sMsg += "\n" + sOptionalMsg
            # endfor
            if sMsg is not None:
                raise CAnyError_Message(sMsg=f"accumulated checking error msg:\n ({sMsg})")
            # endif raise
        # endif

        if sMsg is not None:
            raise CAnyError_Message(sMsg=sMsg)
        # endif raise

    # endif some checks for required field

    if isinstance(_xValueDefault, COptionField):
        # do some checks
        if isinstance(_xValue, COptionField):
            if _xValueDefault.xDefaultOption is None:
                raise CAnyError_Message(
                    sMsg=f"ParameterField({_sFieldName}) of <{cls}> was not given, but for that option,"
                    " no default was given. A value is required in dict field"
                )
            # endif raise

            _xValue = _xValueDefault.xDefaultOption
        else:
            if _xValue not in _xValueDefault.xTypeOptionArg:
                raise CAnyError_Message(
                    sMsg=f"ParameterField({_sFieldName}) of <{cls}>: "
                    f"given Option '{_xValue}' is not in Options({_xValueDefault.xTypeOptionArg})"
                )
            # endif raise

        # endif

    # endif some checks for option field

    return _xValue


# enddef


# end def (_handleDefault)


###########################################################################################################
###########################################################################################################
###########################################################################################################


# some tests during development
if __name__ == "__main__":

    from inspect import currentframe
    from anybase import assertion
    from typing import Any

    from anybase.dec.cls_typed_tuple import typedTuple

    def _PrintTestFrame():
        cf = currentframe()
        print(f"-- Test in {cf.f_back.f_back.f_code.co_filename}[{cf.f_back.f_back.f_lineno}] ")

    # enddef

    assertion.Enable()
    print("\n---paramclass Test-Cases--------------------------------------------------------------")
    print("--------------------------------------------------------------------------------------\n")

    lTestHandlers = []

    def RegisterCallHandler(_xCallFunction):
        lTestHandlers.append(_xCallFunction)

    # enddef decorator

    @typedTuple
    class CImplementationTest:
        xFunction: Any
        bShouldBeOK: bool
        bShowEx: bool

    lImplementHandlers = []

    def RegisterImplementHandler(_xArgument_bShouldBeOK, _xArgument_bShowEx=False):
        def decorator(_xRealFunction):
            lImplementHandlers.append(
                CImplementationTest(
                    xFunction=_xRealFunction,
                    bShouldBeOK=_xArgument_bShouldBeOK,
                    bShowEx=_xArgument_bShowEx,
                )
            )

        # enddef decorator

        return decorator

    # enddef decorator_factory

    def _TestImplementation(xImplementation: CImplementationTest):
        bExThrown = False
        try:
            xImplementation.xFunction()
        except Exception as xEx:
            bExThrown = True
            if xImplementation.bShouldBeOK:
                sMsg = f"TEST_FAILS: implementation fails with {xEx}"
            else:
                sMsg = "implementation fails as expected" + (f" with \n{xEx}" if xImplementation.bShowEx else "")

        print(
            f"-- Test in {xImplementation.xFunction.__code__.co_filename}"
            f"[{xImplementation.xFunction.__code__.co_firstlineno}] "
        )
        if not bExThrown:
            sMsg = (
                "correct implementation"
                if xImplementation.bShouldBeOK
                else "TEST_FAILS Implementation didn't raise an exception"
            )

        print(f" --> {sMsg} ")
        print("-----------------------------------------------------------------\n")

    # enddef

    def TestParamClass(cls, _dicArgs, _bEverythingShouldBeOK, _bShowEx=False):
        bExThrown = False
        try:
            dataObject = cls(_dicArgs)
        except Exception as xEx:
            bExThrown = True
            if _bEverythingShouldBeOK:
                sMsg = f"TEST_FAILS: {cls} fails with {xEx}"
            else:
                if _bShowEx:
                    sMsg = f"{cls} fails with {xEx}\n!! AS EXPECTED !!"
                else:
                    sMsg = f"{cls} fails as expected"

        _PrintTestFrame()
        if not bExThrown:
            print(f"test for {cls} produces:\n{dataObject}")
            if _bEverythingShouldBeOK:
                sMsg = f"{cls} accepts dictionary"
            else:
                sMsg = f"TEST_FAILS {cls} didn't raise an exception"

        print(f" --> {sMsg} ")
        print("-----------------------------------------------------------------\n")

    # enddef TestParamClass

    ###########################################################################################################

    # ------------------------------------------------------------------------------
    # DEPRICATED Field
    # ------------------------------------------------------------------------------
    @RegisterCallHandler
    def _():
        dicArgs = {
            "xValue": ["45", "3.1415", "-987"],  # too long
            "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
        }

        @paramclass
        class CDeltaRotationEulerParams:
            lValue: list = (CParamFields.REQUIRED([float, float, float]), CParamFields.DEPRECATED("xValue"))

        TestParamClass(CDeltaRotationEulerParams, dicArgs, True, _bShowEx=True)

    # ------------------------------------------------------------------------------
    # list[float,float,float] Tests
    # ------------------------------------------------------------------------------
    @paramclass
    class CParamList3F32:
        lOffset: list[float, float, float] = CParamFields.REQUIRED()

    @RegisterCallHandler
    def _():
        dicArgs = {
            "lOffset": ["45", "3.1415", "-987", 12, 12, 123],  # too long
            "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
        }
        TestParamClass(CParamList3F32, dicArgs, False, _bShowEx=True)

    @RegisterCallHandler
    def _():
        dicArgs = {
            "lOffset": ["45", "3.1415"],  # too short
            "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
        }
        TestParamClass(CParamList3F32, dicArgs, False)

    @RegisterCallHandler
    def _():
        dicArgs = {
            "_lOffset": ["45", "3.1415"],  # not there
            "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
        }
        TestParamClass(CParamList3F32, dicArgs, False)

    # ------------------------------------------------------------------------------
    @RegisterCallHandler
    def _():
        @paramclass
        class CParamList:
            # list_gen: list  # = CParamFields.HINT("sollte auch verboten sein")
            lOffset_2: list[float, float, float] = CParamFields.REQUIRED()
            lOffset: list[float] = CParamFields.DEFAULT([42])
            # lOffset: list[float, float, float] = CParamFields.DEFAULT([0.0, 0.0, 1.0])
            # list_f32: list[float] not allowed, when not required, at least default value must be given
            list_genDefault: list = CParamFields.DEFAULT([0.0, 0.0, 1.0])
            list_f32String: list[float] = CParamFields.DEFAULT([3.1415, "10.0", -99])
            list_genDefaultString: list = CParamFields.DEFAULT("Dirk")

        dicArgs = {
            "lOffset": 3.1415,
            "_lOffset_2": "INIT",
            "lOffset_2": ["45", "3.1415", "-987", 12, 12, 123],
            "list_f32": [1, 9],
            "list_gen": [1, 9],
            "list_genDefault": [1, 9],
            "list_f32String": [1, 9],
            "list_genDefaultString": [1, 9],
            "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
        }

        # TestParamClass(CParamList, dicArgs, True)

    # for xCallFunction in lTestHandlers:
    #     xCallFunction()

    ###########################################################################################################

    # ------------------------------------------------------------------------------
    # list Implementation Tests
    # ------------------------------------------------------------------------------
    @RegisterImplementHandler(False, True)
    def _():
        @paramclass
        class CParamList_notAlias:
            lScale: list = CParamFields.REQUIRED([float, float, float], (list, tuple))  # this is not a GenericAlias

    @RegisterImplementHandler(False, True)
    def _():
        @paramclass
        class CParamList3F32_Req2:
            fOffset: float = (
                CParamFields.REQUIRED(list[float]),
                CParamFields.DEFAULT(3.1415),
                CParamFields.HINT("Position offset for evaluated positions"),
            )

    @RegisterImplementHandler(False)
    def _():
        @paramclass
        class CParamList3F32_Req2:
            fOffset: float = CParamFields.REQUIRED(list[float])

    @RegisterImplementHandler(False)
    def _():
        @paramclass
        class CParamList3F32_Req2:
            lOffset: list[float, float, float] = CParamFields.REQUIRED(list[float, float])

    @RegisterImplementHandler(True)
    def _():
        @paramclass
        class CParamList3F32_Req:
            lOffset: list[float, float, float] = CParamFields.REQUIRED()
            lScale: list = CParamFields.REQUIRED(list[float, float, float], (int, float))

    @RegisterImplementHandler(False)
    def _():
        @paramclass
        class CParamList3F32_Default:
            lOffset: list[float, float, float] = (
                CParamFields.DEFAULT([0, 0]),
                CParamFields.HINT("Position offset for evaluated positions"),
            )

    @RegisterImplementHandler(True)
    def _():
        @paramclass
        class CParamList3F32_Default:
            lOffset: list[float, float, float] = (
                CParamFields.DEFAULT([1, 0, 0]),
                CParamFields.HINT("Position offset for evaluated positions"),
            )

    @RegisterImplementHandler(False, True)
    def _():
        @paramclass
        class CParamList3F32_DefaultReq:
            lScale: list = (
                CParamFields.REQUIRED(list[float, float, float], (int, float)),
                CParamFields.DEFAULT([0, 0]),
            )

    @RegisterImplementHandler(True)
    def _():
        @paramclass
        class CParamList3F32_DefaultOption:
            lScale_42: list[float] = (CParamFields.DEFAULT([42, 3]),)

    @RegisterImplementHandler(True)
    def _():
        @paramclass
        class CParamList3F32_DefaultOption:
            lScale_42: list[float] = (CParamFields.DEFAULT(42),)
            lScale_vec: list = (CParamFields.DEFAULT([23, 98, 12]),)
            lScale_vecString: list[float] = (CParamFields.DEFAULT(["23", "98", "12"]),)

    for xImplementation in lImplementHandlers:
        _TestImplementation(xImplementation)

    @paramclass
    class CParamList:
        # list_gen: list  # = CParamFields.HINT("sollte auch verboten sein")
        lOffset_2: list[float, float, float] = CParamFields.REQUIRED()
        lOffset: list[float] = CParamFields.DEFAULT(42)
        lOffset_42: list[float] = CParamFields.DEFAULT(42)
        # lOffset: list[float, float, float] = CParamFields.DEFAULT([0.0, 0.0, 1.0])
        # list_f32: list[float] not allowed, when not required, at least default value must be given
        list_genDefault: list = CParamFields.DEFAULT([0.0, 0.0, 1.0])
        list_f32String: list[float] = CParamFields.DEFAULT([3.1415, "10.0", -99])
        list_genDefaultString: list = CParamFields.DEFAULT("Dirk")

    dicArgs = {
        "lOffset": 3.1415,
        "_lOffset_2": "INIT",
        "lOffset_2": ["45", "3.1415", "-987"],
        "list_f32": [1, 9],
        "list_gen": [1, 9],
        "list_genDefault": [1, 9],
        "list_f32String": [1, 9],
        "list_genDefaultString": [1, 9],
        "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
    }

    dataList = CParamList(dicArgs)

    print(dataList)

    @paramclass
    class CParamVector:
        xModule: str = CParamFields.REQUIRED(str)
        lLocation: list = CParamFields.REQUIRED(list[float, float, float], float)
        lOffset: list[float, float, float] = CParamFields.DEFAULT([0.0, 0.0, 1.0])

        sMode: str = CParamFields.OPTIONS(["INIT", "FRAME_UPDATE"], xDefault="INIT")
        sUnit: str = CParamFields.DEFAULT("rad")

        pass

    # end class

    dicArgs = {
        "xModule": 3.1415,
        "sMode": "INIT",
        "lOffset": [1, 9],
        "falsch": True,
        "lLocation": "1",
        "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
    }
    data2 = CParamVector(dicArgs)

    # @paramclass
    # class CParam:
    #     sDTI: str = (
    #         paramFields.HINT(sHint="wertvoller Hinweis"),
    #         paramFields.REQUIRED("label"),
    #     )
    #     xModule: str = None
    #     sMode: str = paramFields.OPTIONS(["INIT", "FRAME_UPDATE"], xDefault="INIT")
    #     sUnit: str = "rad"
    #     # sLengthV3: list = [1, 2, 3] # error -> mutables for default, das kann zu schwerer Irritationen führen
    #     sLengthV3: list = paramFields.DEFAULT([1, 2, 3])
    #     sVeryImportant: str = (
    #         paramFields.HINT(sHint="ohne dich kann ich nicht leben"),
    #         paramFields.REQUIRED(),
    #     )
    #     xRotAxis: list = paramFields.REQUIRED(
    #         [int, float, str]
    #     )  # der Nutzer ist gezwungen eine Liste anzugeben, Default listen ueber mutable lVector = [1,2,3] ist nicht gut, gibt sogar ERROR

    #     pass

    @paramclass
    class CGeoPlacementMapParams:
        sDTI: str = (
            CParamFields.REQUIRED("/catharsys/blender/modify/object/geometric-placement-map:1.1"),
            CParamFields.DISPLAY("Keyword-String"),
            CParamFields.DEPRECATED("DTI"),
        )
        sDisplay_sDTI: str = None  # will be filled with live automatically, used for autocomplete
        # raises exception !!typo sdti!! sDisplay_sdti: str = None  # will be filled with live automatically, used for autocomplete

        sMode: str = CParamFields.OPTIONS(["INIT", "FRAME_UPDATE"], xDefault="INIT")
        fMaxObjectHeight: float = (
            CParamFields.DEFAULT(1.8),
            CParamFields.DISPLAY("maximum Object Height"),
            CParamFields.HINT("objects with that height should be placed even if they are in a box"),
        )
        sNotGiven: str = None
        # sNotGiven2: str ##>>  will raise an exception
        # onlyDeclaration = "ede"  ##>>  will raise an exception

        # test bDoSomething is given as bool
        # bDoSomethingElse is given as integer iDoSomethingElse
        bDoSomething: bool = (
            CParamFields.HINT("bool Object, given as bool in test dict"),
            CParamFields.DEFAULT(False),
        )

        bDoSomethingElse: bool = (
            CParamFields.HINT("bool Object, given as integer in test dict"),
            CParamFields.DEFAULT(True),
        )

        fObjectRadius: float = (
            CParamFields.DEFAULT(0.4),
            CParamFields.HINT("objects with that radius should be placed next to an obstacle"),
        )
        iGeometricID: int = CParamFields.HINT("test ID!")

        sGeometricVertexGroupName: str = CParamFields.HINT(
            "if given, that field already exists and contains the weights, otherwise it will be generated automatically"
        )
        sCameraVertexGroupName: str = CParamFields.HINT(
            "if given, that field already exists and contains the weights, otherwise it will be generated automatically"
        )
        sObstacleClnName: str = CParamFields.HINT(
            "all these obstacles will throw a sight shadow onto geometric placement maps for the given camera"
        )
        sCameraName: str = CParamFields.HINT(
            "if given, that camera is used for generating the visibility map, otherwise the active camera from bpy is requested"
        )
        vecParams: CParamVector = None

        def __post_init__(self, _dictArgs):
            print("hier kann noch individuell was passieren")

        def aFunc(self):
            print("aFunc")

        # enddef
        # endclass

        # end def

        def react(self, dictArgs):
            try:
                if hasattr(self, "__post_init__"):
                    self.__post_init__(_dictArgs=dicArgs)
                # end if
            except Exception as xEx:
                sMsg = "rad2hi hier passiert was schlimmes, hier ist die Ursache"
                raise CAnyError_Message(sMsg=sMsg, xChildEx=xEx)
            # endtry

            lField_defaults = [xField for xField in dataclasses.fields(self) if xField.name.endswith("_default")]
            lField_names = [xField.name for xField in dataclasses.fields(self) if not xField.name.endswith("_default")]
            for xDefaultField in lField_defaults:
                self.__setattr__(xDefaultField.name[2:-8], xDefaultField.default)
            # end for
            for sName, xValue in dictArgs.items():
                if sName in lField_names:
                    type_cast = lField_defaults[lField_names.index(sName)].type
                    xValueCasted = convert.ToType(xValue, lField_defaults[lField_names.index(sName)].type)
                    self.__setattr__(sName, xValueCasted)
                # end if
            # end for

            for xDefaultField in lField_defaults:
                sName = xDefaultField.name[2:-8]
                type_cast = lField_defaults[lField_names.index(sName)].type
                xValue = getattr(self, sName)
                # xValue = _handleDefault(
                #     "CGeoPlacementMapParams", sName, type_cast(xValue), type_cast(xDefaultField.default)
                # )
                xValue = _handleDefault(CGeoPlacementMapParams, self, dictArgs, sName, xValue, xDefaultField.default)
                self.__setattr__(sName, xValue)
            # end for

            # bool check
            lField_names_bool = [sName for sName in lField_names if sName.startswith("b")]
            for sBoolName in lField_names_bool:
                sIntegerBoolName = "i" + sBoolName[1:]
                if sIntegerBoolName in dicArgs:
                    if sIntegerBoolName in lField_names:
                        raise CAnyError_Message(sMsg=f"ParameterField <{sIntegerBoolName}> AND <{sBoolName}> exists")
                    # end if
                    if sBoolName in dicArgs:
                        raise CAnyError_Message(sMsg=f"dictionary contains both <{sIntegerBoolName}> AND <{sBoolName}>")
                    # end if
                    iBoolCasted = convert.ToType(dicArgs[sIntegerBoolName], int)
                    self.__setattr__(sBoolName, iBoolCasted > 0)
                # end deprecated integer to bool
            # end for all bool fields

        # end def

    def raiseError():
        print("!!raiseError")

        try:
            data2.react(dicArgs)
        except Exception as xEx:
            sMsg = "rad2hi hier passiert was schlimmes, hier ist die Ursache"
            raise CAnyError_Message(sMsg=sMsg, xChildEx=xEx)
        # endtry

    def DeltaRotationEuler(dicArgs):
        """test"""
        print("test")

        # data = CParam(dicArgs)
        dicArgs["sDTI"] = "/catharsys/blender/modify/object/geometric-placement-map:1.0"

        try:
            data2 = CGeoPlacementMapParams(dicArgs)
            data2.react(dicArgs)
        except Exception as xEx:
            sMsg = "was ist denn hier schief gegangen in Param Decorator"
            raise CAnyError_Message(sMsg=sMsg, xChildEx=xEx)
        # endtry
        # enddef

        print(f"wie sieht wohl vecParam aus? '{data2.vecParams}'")

        try:
            raiseError()
        except Exception as xEx:
            sMsg = "rad2hi Error executing level 2"
            raise CAnyError_Message(sMsg=sMsg, xChildEx=xEx)
        # endtry

    # end def

    dicArgs = {
        "value": "blender/animate/object/rotate/const:1",
        "hint": "entry point identification",
        "DTI": "/catharsys/blender/modify/object/geometric-placement-map:1.0",
        "sID": "/catharsys/blender/modify/object/geometric-placement-map:1.0",
        "sMode": "FRAME_UPDATE",
        # handling bools (default bXXX)
        "bDoSomething": True,
        # handling alternative bool: inside paramclass bDoSomethingElse erkennt trotzdem iXXX
        # -> warning Deprecated !! not really readable
        "iDoSomethingElse": 0,
        # "bDoSomethingElse": True,
        "_sUnit": "entry point identification",
        "sVeryImportant": "this must be given",
        "xRotAxis": [0, 0, 1],
        "vecParams": {"xModule": "xModule", "sMode": "INIT", "falsch": True},
        "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
    }

    kwArgs = {
        "__locals__": {"filepath": "blender/animate/object/rotate/const:1"},
        "blender": "label",
        "forEachCfg": "entry point identification",
        "render": {"xModule": "xModule", "sMode": "Sonicht", "falsch": True},
    }

    # try:
    #     raiseError()
    # except Exception as xEx:
    #     sMsg = "rad2hi Error calling function"
    #     raise CAnyError_Message(sMsg=sMsg, xChildEx=xEx)
    # # endtry

    #    data2: CGeoPlacementMapParams = CreateParam(CGeoPlacementMapParams, dicArgs, kwArgs)
    data2 = CGeoPlacementMapParams(dicArgs)

    try:

        DeltaRotationEuler(dicArgs=dicArgs)
    except Exception as xEx:
        sMsg = "rad2hi Error executing Level 1"
        raise CAnyError_Message(sMsg=sMsg, xChildEx=xEx)
    # endtry
