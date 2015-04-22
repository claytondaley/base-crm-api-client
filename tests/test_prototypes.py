#!/usr/bin/env python
"""Test the functionality of Prototypes"""
from copy import copy

import logging
from pprint import pprint

logger = logging.getLogger(__name__)

from mock import Mock
from nose.tools import assert_raises, eq_
from prototype import Resource
from tests.test_common import SAMPLES

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
        object_.__setattr__(attribute, value)
        eq_(getattr(object_, attribute), value)


def setattr_attributeerror(object_, attribute, value):
    assert_raises(AttributeError, object_.__setattr__, attribute, value)


def setattr_keyerror(object_, attribute, value):
    assert_raises(KeyError, object_.__setattr__, attribute, value)


def setattr_typeerror(object_, attribute, value):
    assert_raises(TypeError, object_.__setattr__, attribute, value)


class PropertiesStub(Resource):
    PROPERTIES = {
        '_readonly': object,
        'editable': object,
    }


def test_resource_setattr_readonly():
    """
    Readonly attributes are indicated by a leading underscore and should throw a KeyError
    """
    stub = PropertiesStub()
    mock = Mock()
    yield setattr_keyerror, stub, 'readonly', mock


def test_resource_setattr_editable():
    """
    Editable attributes do not have a leading underscore and are stored inside the 'dirty' table
    """
    stub = PropertiesStub()
    mock = Mock()
    yield setattr_eq, stub, 'editable', mock


def test_resource_setattr_nonproperty():
    """
    If an attribute is not a member of properties, an AttributeError should be generated
    """
    stub = PropertiesStub()
    mock = Mock()
    yield setattr_attributeerror, stub, 'nonproperty', mock


def test_generator_setattr_typechecking():
    """
    setattr should provide type checking based on PROPERTIES definition
    """
    for type in SAMPLES:
        mock = Mock(Resource)
        object.__setattr__(mock, 'PROPERTIES', {'key': type})
        object.__setattr__(mock, '_dirty', dict())
        for t2, samples in SAMPLES.iteritems():
            if not isinstance(t2, type):
                for sample in samples:
                    yield setattr_eq, mock, 'key', sample
            else:
                for sample in samples:
                    yield setattr_typeerror, mock, 'key', sample


def is_attribute_unchanged_data(value):
    mock = Mock(Resource)
    object.__setattr__(mock, 'PROPERTIES', {'key': object})
    object.__setattr__(mock, '_data', {'key': value})
    object.__setattr__(mock, '_dirty', dict())
    mock.key = value
    assert 'key' not in mock._dirty


def test_generator_is_attribute_unchanged():
    """
    If an attribute is unchanged, we should not store it in 'dirty'.  This should use the 'is' operator to preserve
    mutability.
    """
    for value in [v[0] for k, v in SAMPLES.iteritems()]:
        yield is_attribute_unchanged_data, value


EQ_NOT_IS = [
    [1000000, 10 ** 6],
    [[0, 1], [0, 1]],
    [{}, {}],
    [{'key': 'value'}, {'key': 'value'}]
]


def eq_attribute_changed_data(value, compare):
    # sample values are equal
    assert value == compare
    # sample values are not the same
    assert value is not compare
    mock = Resource()
    object.__setattr__(mock, 'PROPERTIES', {'key': object})
    mock.key = compare
    assert 'key' in mock._dirty
    # Confirm that the key is updated
    assert mock.key is compare
    assert mock.key is not value


def test_generator_equal_attribute_replace():
    """
    If an attribute is equal but not "is", we need to update it to preserve mutability.
    """
    for values in EQ_NOT_IS:
        yield eq_attribute_changed_data, values[0], values[1]