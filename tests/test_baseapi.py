__author__ = 'Clayton Daley'

from client import BaseAPI
from mock import Mock
from nose.tools import assert_raises
from prototypes import Resource, BaseCrmAuthentication


def mock_auth():
    mock = Mock(BaseCrmAuthentication)
    mock.headers.return_value = dict()
    return mock


def test_save_without_change():
    """
    If the resource has no changes, save() should throw an error
    """
    auth = mock_auth()
    base = BaseAPI(auth)
    # Resource without change
    resource = Mock(Resource)
    resource.id = 1
    resource.params.return_value = dict()
    assert_raises(ValueError, base.save, resource)


def test_create_without_change():
    """
    If the resource has no changes, create() should throw an error
    """
    auth = mock_auth()
    base = BaseAPI(auth)
    resource = Mock(Resource)
    resource.id = None
    resource.params.return_value = dict()
    assert_raises(ValueError, base.create, resource)
