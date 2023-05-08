#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \CheckFuncTypes.py
# Created Date: Wednesday, May 25th 2022, 11:51:33 am
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

import dataclasses
from typing import Any


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


#################################################################################################
#################################################################################################
class CReadOnly(type):
    def __setattr__(self, __name: str, __value) -> None:
        raise ValueError(f"{self}: do not change attribute: '{__name}'")

    # enddef


# end class


_FIELDS = "__tt_FIELDS__"
_ORIGINAL_CLASS_NAME = "__tt_class_name"


def _ProcessTypedTuple(cls):
    """this wrapper is similiar to dataclasses implementation of the python lib"""
    # Now that dicts retain insertion order, there's no reason to use
    # an ordered dict.  I am leveraging that ordering here, because
    # derived class fields overwrite base class fields, but the order
    # is defined by the base class, which is found first.

    dicClsAnnotations = cls.__dict__.get("__annotations__", {})
    __checkAnnotations(cls, dicClsAnnotations)

    # Now find fields in our class.  While doing so, validate some
    # things, and set the default values (as class attributes) where
    # we can.
    lClsFields = [
        dataclasses._get_field(cls, a_name=sName, a_type=xType, default_kw_only=None)
        for sName, xType in dicClsAnnotations.items()
    ]

    # Do we have any Field members that don't also have annotations?
    for sName, xValue in cls.__dict__.items():
        if isinstance(xValue, dataclasses.Field) and sName not in dicClsAnnotations:
            raise TypeError(f"'{sName}' is a field but has no type annotation")
        # endif
    # end for

    # Remember all of the fields on our class (including bases).  This
    # also marks this class as being a dataclass.
    dicNamedTupleAttributes = {}
    for xField in lClsFields:
        sName = xField.name
        xType = xField.default
        dicNamedTupleAttributes[sName] = xType

    setattr(cls, _FIELDS, lClsFields)

    class CTypedTuple(cls, metaclass=CReadOnly):
        __tt_class_name = f"{cls}"

        def __init__(self, **_KwArgs) -> None:
            self._duringInit = True
            lFields: list
            lFields = getattr(cls, _FIELDS)

            lsKeys = []
            for xField in lFields:
                sKey = xField.name
                lsKeys.append(sKey)

                xDefault = xField.default
                xType = xField.type

                xValue = _KwArgs.get(sKey)
                if xValue is None:
                    if isinstance(xDefault, type(dataclasses.MISSING)):
                        raise ValueError(f"{cls} expected kwArg({sKey}) but is not given")
                    # endif
                    setattr(self, sKey, xDefault)
                else:
                    # handles lists
                    if hasattr(xType, "__args__"):
                        xType_args = xType.__args__
                        if len(xValue) != len(xType_args):
                            raise ValueError(
                                f"{cls} for kwArg({sKey}) the type {xType} requires #{len(xType_args)} values"
                                f" but #{len(xValue)} were given"
                            )
                        # endif

                        # check each element for correct type
                        for i in range(0, len(xValue)):
                            bSameInstance = isinstance(type(xValue[i]), xType_args[i])
                            bXArgsTypeIsNumber = xType_args[i] is float or xType_args[i] is int
                            bAreNumbers = isinstance(xValue[i], (int, float)) and bXArgsTypeIsNumber
                            if not bSameInstance and not bAreNumbers:
                                raise ValueError(
                                    f"{cls} for kwArg({sKey}) incompatible types inside arg#{i}"
                                    f" the types {type(xValue[i])} -  {xType_args[i]}"
                                )
                            # endif
                        # end for list elements

                        # convert tuple and list given into that what was expected
                        xResultType = type(xType())
                        setattr(self, sKey, xResultType(xValue))

                    elif xType is Any or isinstance(xValue, xType):
                        setattr(self, sKey, xValue)
                    else:
                        raise ValueError(
                            f"{cls} for kwArg({sKey}) the type {xType} is expected but {type(xValue)} was given"
                        )
                    # end if
                # end if
            # end for each field

            for sKey in _KwArgs.keys():
                if sKey not in lsKeys:
                    raise ValueError(f"{cls} has no attribute {sKey}, wrong initialistion parameter list")
                # end if
            # end for each keyword

            self._duringInit = False

        # end def

        def __setattr__(self, __name: str, __value) -> None:
            if __name == "_duringInit" or self._duringInit:
                self.__dict__[__name] = __value
            else:
                raise ValueError(f"{self.__tt_class_name}: do not change attribute: '{__name}'")
            # endif

        # enddef

    # end internal class

    return CTypedTuple


# end def

# .....................................................................................................
# .....................................................................................................


def typedTuple(cls=None):
    """
    this wrapper is similiar to dataclasses implementation of the python lib

    Returns the same class as was passed in, but with class vars that are strings
    (It might remember to an enum, and it is possible to use enum class and a
    specialisation of enum, that prints automatically their names as strings,
    but with that construct, dicts cannot be accessed)

    Usage:
        @typedTuple
        class CResultOfAlgoX:
            bOK: bool
            sDTI: str           !! annotation is mandatory
            xModule: Any        !! xModule hasn't got an annotation check, that means any value can be assigned
            lVector: list[float, float,float]        !! lVector must be initialised with a list of 3 floats
            lpos: list[float, float] = [23.9, 234.9] !! is not allowed, defaults of mutables are not a very good idea
            tPos: tuple[float, float] = (43, 43) !! that is allowed, (43,43) is not mutable
                                # a) assigning floats to int and int to floats will be casted without remarks
                                # b) assigning values to tuple or list can be done with the opposite type,
                                #      these collections will be casted automatically to their counterpart if necessary
            sVeryImportant  = "VIP"  !! it fails because it hasn't got an annotation and it has an assignment

        t1 = CFoo( fooParams )
        t2 = CResultOfAlgoX(sDTI="actionDefinition", bOK=True, lVector=[4, 6],
                            tPos=[34, 98], dDict={"test": True}, xModule=t1)

    """

    def wrap(cls):
        return _ProcessTypedTuple(cls)

    # end def internal wrapper

    # See if we're being called as @constKeywordNamespace or @constKeywordNamespace().
    if cls is None:
        # We're called with parens.
        return wrap
    # end if

    # We're called as @constKeywordNamespace without parens.
    return wrap(cls)


# end def

###########################################################################################################
###########################################################################################################
###########################################################################################################

# some tests during development
if __name__ == "__main__":

    try:

        @typedTuple
        class CTypedParamErrorness:
            bOK: bool
            sDTI: str
            xModule: str = None
            sVeryImportant: Any = None
            sOK = None

        # end class

    except Exception as xEx:
        print(f"correct handling of keyword class raises Exception {str(xEx)}")
    # end try failure

    @typedTuple
    class CTypedParam1:
        bOK: bool
        sDTI: str
        # lpos: list[float, float] = [23.9, 234.9] is not allowed,
        # defaults of mutables are not a very good idea and causes errors
        xModule: str = None
        sVeryImportant: Any = None

    # end class

    @typedTuple
    class CTypedParam2:
        bOK: bool
        lVector: list[float, float, float]
        tPos: tuple[float, float] = (43, 43)
        dDict: dict
        xModule: CTypedParam1

    # end class

    t1 = CTypedParam1(sDTI="True", bOK=True, xModule="module_aplha")
    t2 = CTypedParam2(bOK=True, lVector=[4, 5, 6], tPos=(34, 98), dDict={"test": True}, xModule=t1)
    t3 = CTypedParam2(bOK=True, lVector=[4, 5, 6], dDict={"test": True}, xModule=t1)
    print("test zu ende")
