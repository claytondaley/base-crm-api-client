#!/usr/bin/env python
"""Test the functionality of Prototypes"""

import logging
logger = logging.getLogger(__name__)

from mock import Mock
from nose.tools import assert_raises, eq_
from prototypes import Resource

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


def getattr_attributeerror(object_, attribute):
    assert_raises(AttributeError, getattr, object_, attribute)


def getattr_keyerror(object_, attribute):
    assert_raises(KeyError, getattr, object_, attribute)


def getattr_typeerror(object_, attribute):
    assert_raises(TypeError, getattr, object_, attribute)


def setattr_eq(object_, attribute, value):
        setattr(object_, attribute, value)
        eq_(object_.__dict__['dirty'][attribute], value)


def setattr_attributeerror(object_, attribute, value):
    assert_raises(AttributeError, setattr, object_, attribute, value)


def setattr_keyerror(object_, attribute, value):
    assert_raises(KeyError, setattr, object_, attribute, value)


def setattr_typeerror(object_, attribute, value):
    assert_raises(TypeError, setattr, object_, attribute, value)


class ResourceStub(Resource):
    PROPERTIES = {
        '_readonly': object,
        'editable': object,
        'int': int,
        'basestring': basestring,
        'list': list,
        'dict': dict,
        'mock': Mock,
        'rules': {

        }
    }

SAMPLES = {
    'int': 23,
    'basestring': 'a special string for you',
    'list': ['a', 'b', 'z'],
    'dict': {'a': 1, 'b': 'two', 'c': Mock()},
    'mock': Mock(),
}


def test_resource_setattr_readonly():
    """
    Readonly attributes are indicated by a leading underscore and should throw a KeyError
    """
    stub = ResourceStub()
    mock = Mock()
    assert_raises(KeyError, setattr, stub, 'readonly', mock)


def test_resource_setattr_editable():
    """
    Editable attributes do not have a leading underscore and are stored inside the 'dirty' table
    """
    stub = ResourceStub()
    mock = Mock()
    stub.editable = mock
    assert stub.__dict__['dirty']['editable'] is mock


def test_resource_setattr_nonproperty():
    """
    If an attribute is not a member of properties, an AttributeError should be generated
    """
    stub = ResourceStub()
    mock = Mock()
    assert_raises(AttributeError, setattr, stub, 'nonproperty', mock)


def test_generator_typechecking_setattr():
    """
    setattr should provide type checking based on PROPERTIES definition
    """
    for type in SAMPLES:
        # Non-matching types should result in TypeError
        for sample in {k: SAMPLES[k] for k in SAMPLES if k != type}:
            stub = ResourceStub()
            yield setattr_typeerror, stub, type, SAMPLES[sample]
        stub = ResourceStub()
        # Matching types should get set to stub.dirty
        yield setattr_eq, stub, type, SAMPLES[type]