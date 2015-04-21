#!/usr/bin/env python
"""Test the functionality of Prototypes"""

import logging
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
        setattr(mock, 'PROPERTIES', {'key': type})
        setattr(mock, '_dirty', dict())
        for t2, samples in SAMPLES.iteritems():
            if not isinstance(t2, type):
                for sample in samples:
                    yield setattr_eq, mock, 'key', sample
            else:
                for sample in samples:
                    yield setattr_typeerror, mock, 'key', sample