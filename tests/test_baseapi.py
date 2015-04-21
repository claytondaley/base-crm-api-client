#!/usr/bin/env python
"""Test the functionality of BaseAPI"""

import logging
logger = logging.getLogger(__name__)

from client import BaseAPI
from mock import Mock
from nose.tools import assert_raises
from prototype import Resource, BaseCrmAuthentication, Collection

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


def mock_auth():
    mock = Mock(BaseCrmAuthentication)
    mock.headers.return_value = dict()
    return mock


def test_get_without_resource_typeerror():
    """If entity= is not a Resource, get() should raise TypeError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    # Resource without change
    resource = Mock(Collection)
    # Must have an ID to bypass check
    assert_raises(TypeError, base.get, resource)


def test_get_without_id_valueerror():
    """If the resource has no changes, get() should raise ValueError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    # Resource without change
    resource = Mock(Resource)
    # Must have an ID to bypass check
    resource.id = None
    assert_raises(ValueError, base.get, resource)


def test_save_without_resource_typeerror():
    """If entity= is not a Resource, save() should raise TypeError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    # Resource without change
    resource = Mock(Collection)
    # Must have an ID to bypass check
    assert_raises(TypeError, base.save, resource)


def test_save_without_change_valueerror():
    """If the resource has no changes, save() should raise ValueError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    # Resource without change
    resource = Mock(Resource)
    # Must have an ID to bypass check
    resource.id = 1
    resource.get_data.return_value = dict()
    assert_raises(ValueError, base.save, resource)


def test_save_without_id_valueerror():
    """If the resource has no changes, save() should raise ValueError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    # Resource without change
    resource = Mock(Resource)
    # Must have an ID to bypass check
    resource.id = None
    assert_raises(ValueError, base.save, resource)


def test_create_without_resource_typeerror():
    """If entity= is not a Resource, create() should raise TypeError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    # Resource without change
    resource = Mock(Collection)
    # Must have an ID to bypass check
    assert_raises(TypeError, base.create, resource)


def test_create_without_change_valueerror():
    """If the resource has no changes, create() should raise ValueError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    resource = Mock(Resource)
    # Must not have an ID to bypass check
    resource.id = None
    resource.get_data.return_value = dict()
    assert_raises(ValueError, base.create, resource)


def test_create_with_id_valueerror():
    """If the resource has no changes, create() should raise ValueError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    resource = Mock(Resource)
    # Must not have an ID to bypass check
    resource.id = 1
    assert_raises(ValueError, base.create, resource)


def test_delete_without_resource_typeerror():
    """If entity= is not a Resource, create() should raise TypeError"""
    auth = mock_auth()
    base = BaseAPI(auth)
    # Resource without change
    resource = Mock(Collection)
    # Must have an ID to bypass check
    assert_raises(TypeError, base.delete, resource)


