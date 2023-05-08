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


def _ProcessConstKeywordNamespace(cls):
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
        dataclasses._get_field(cls, a_name=sName, a_type=xType, default_kw_only=None)
        for sName, xType in dicClsAnnotations.items()
    ]

    for xField in lClsFields:
        sName = xField.name
        sValue = sName

        # #---- str annotation -------
        if xField.type != str:
            raise TypeError(f"Keyword '{sName}' of <{cls}> must be given with annotation str")
        # endif

        dicFields[sName] = xField
        # fields[name].default = name

        # #---- MISSING -------
        if not isinstance(dicFields[sName].default, type(dataclasses.MISSING)):
            if isinstance(dicFields[sName].default, str):
                sValue = dicFields[sName].default
            else:
                raise TypeError(f"Keyword '{sName}' of <{cls}> is given with value, that is not allowed")
            # endif
        # endif

        setattr(cls, sName, sValue)
    # end for

    # Do we have any Field members that don't also have annotations?
    for sName, xValue in cls.__dict__.items():
        if isinstance(xValue, dataclasses.Field) and sName not in dicClsAnnotations:
            raise TypeError(f"'{sName}' is a field but has no type annotation")
        # endif
    # end for

    # Remember all of the fields on our class (including bases).  This
    # also marks this class as being a dataclass.
    setattr(cls, dataclasses._FIELDS, dicFields)

    class CNewClass(cls, metaclass=CReadOnly):
        pass

    # end internal class

    return CNewClass


# end def

# .....................................................................................................
# .....................................................................................................


def constKeywordNamespace(cls=None):
    """
    this wrapper is similiar to dataclasses implementation of the python lib

    Returns the same class as was passed in, but with class vars that are strings
    (It might remember to an enum, and it is possible to use enum class and a
    specialisation of enum, that prints automatically their names as strings,
    but with that construct, dicts cannot be accessed)

    Usage:
        @constKeywordNamespace
        class NsKeywordParam:
            sDTI: str           !! annotation 'str' is mandatory
            xModule: str        !! CKeywordParam.xModule is automatically the string of var name
            sUnit: str = "rad"  !! = "rad" is not allowed, to overcome false assignments
            sVeryImportant  = "VIP"  !! it fails because it hasn't got an annotation and it has an assignment
    """

    def wrap(cls):
        return _ProcessConstKeywordNamespace(cls)

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

        @constKeywordNamespace
        class CKeyWordParam2:
            sDTI: str
            xModule: str = None
            sVeryImportant = None

        # end class

    except Exception as xEx:
        print(f"correct handling of keyword class raises Exception {str(xEx)}")
    # end try failure

    try:

        @constKeywordNamespace
        class CKWParam1:
            sDTI: str
            xBlender: str
            fPixel: str = "rad"

        # end class

    except Exception as xEx:
        print(f"correct handling of keyword class raises Exception {str(xEx)}")
    # end try failure

    @constKeywordNamespace
    class CKWParam2:
        sDTI: str
        sXML: str
        xBase: str
        sLense: str

        def GetModule(cls):
            return 6

        # end def

    # end class 'CORRECT'

    print("test zu ende")
