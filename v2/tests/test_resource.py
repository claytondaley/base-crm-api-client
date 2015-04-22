#!/usr/bin/env python
"""Test the functionality of implemented Resources"""

import logging
logger = logging.getLogger(__name__)

from pprint import pformat
from nose.tools import assert_raises, eq_
from tests.test_common import SAMPLES, COLLECTIONS, RESOURCES
from v2.resource import Person, Contact, Organization, Deal, Lead, Note, Tag, Account, Address, LossReason, Task, \
    DealContact, Pipeline, Source, Stage, User

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


"""
CONFIGURATION
"""


def passes():
    pass


def fail_config(resource, property, message):
    raise Exception("BAD CONFIG (%s.%s):  %s" % (resource, property, message))


def fail_type(resource, attrib, type):
    raise TypeError("Missing test for %s at %s.%s" % (pformat(type), resource.__class__.__name__, attrib))


def test_generate_properties_invalidconfig():
    """
    If a property has an invalid (simple) config, fail the test
    """
    for resource in RESOURCES:
        for property_, type_ in resource.PROPERTIES:
            if isinstance(type_, dict):
                # Indicates a complex config, handled elsewhere
                pass
            elif not issubclass(type_, object):
                yield fail_config, resource, property_, "type %s is not valid" % pformat(type_)
            else:
                # Provide a passing count to offset the failing one
                yield passes


# Complex configuration
def test_generate_properties_invalidconfig():
    """
    If a property has an invalid (complex) config, fail the test
    """
    for resource in RESOURCES:
        for property_ in resource.PROPERTIES:
            if isinstance(property_, dict) and 'in' not in property_ and 'type' not in property_:
                yield fail_config, resource, property_, "either 'in' or 'type' must be set"


def test_test_exists():
    """
    Verify that the prototype tests every type included in the Resource
    """
    for resource in RESOURCES:
        for property_, type_ in resource.PROPERTIES.iteritems():
            if isinstance(type_, dict):
                # Special case config, tested elsewhere
                pass
            elif type_ in SAMPLES:
                # Positive test automatically run
                pass
            else:
                yield fail_type, resource, property_, type_


"""
CONSTRUCTOR BEHAVIOR

This section verifies that constructors follow the standard pattern unless otherwise specified
"""
# Explicitly remove contact from standard constructor tests
STANDARD_CONSTRUCTOR_RESOURCES = [r for r in RESOURCES if r not in [Contact]]


def construct_typeerror(class_, i):
    assert_raises(TypeError, class_, i)


def construct_eq(class_, i):
    resource = class_(i)
    eq_(resource.id, i)


def generator_standard(class_):
    # Standard Classes work on None so you can create() a new instance
    yield construct_typeerror, Contact, None
    # Standard Classes work on valid integers so you can get() an existing record
    for i in range(0, 5):
        yield construct_eq, Contact, i
    # Standard Classes throw TypeError on anything but an int
    yield construct_typeerror, Contact, '1'
    yield construct_typeerror, Contact, 'string'


def test_generator_standard():
    for resource in STANDARD_CONSTRUCTOR_RESOURCES:
        for test in generator_standard(resource):
            yield test


# Special tests for Contact
def test_generator_contact():
    # Contact throws TypeError on None, telling user to use Person or Organization
    yield construct_typeerror, Contact, None
    # Contact works on valid integers since a user could have an ambiguous contact needing get()
    for i in range(0, 5):
        yield construct_eq, Contact, i
    # Contact throws TypeError on anything but an int
    yield construct_typeerror, Contact, '1'
    yield construct_typeerror, Contact, 'string'


"""
Contact (and Inheritors) Mutation Rules
"""


def test_contact_mutate_person():
    """If a contact gets a set_data with is_organization=False, it should mutate to a Person"""
    contact = Contact(1)
    data = {
        'data': {
            'is_organization': False
        }
    }
    contact.set_data(data)
    assert isinstance(contact, Person)


def test_contact_mutate_organization():
    """If a contact gets a set_data with is_organization=True, it should mutate to a Organization"""
    contact = Contact(1)
    data = {
        'data': {
            'is_organization': True
        }
    }
    contact.set_data(data)
    assert isinstance(contact, Organization)


def test_organization_valueerror_not_mutate():
    """An Organization should raise ValueError if it ever gets data with is_organization=False"""
    organization = Organization()
    data = {
        'is_organization': False
    }
    assert_raises(ValueError, organization.format_data_set, data)


def test_person_valueerror_not_mutate():
    """A Person should raise ValueError if it ever gets data with is_organization=True"""
    person = Person()
    data = {
        'is_organization': True
    }
    assert_raises(ValueError, person.format_data_set, data)


"""
Resource conversion from resource/resource_id to Resource
"""


RESOURCE_SET_CONVERSION = {
    'lead': Lead,
    'contact': Contact,
    'deal': Deal,
}


def note_setdata_resource_conversion(resource, id, class_):
    """A Note should convert a resource/resource_id in the data to a Resource"""
    note = Note()
    data = {
        'resource': resource,
        'resource_id': id
    }
    _data = note.format_data_set(data)
    assert isinstance(_data['resource'], class_)


def note_getdata_resource_conversion(instance, resource, resource_id):
    note = Note()
    dirty = {
        'resource': instance
    }
    data = note.format_data_get(dirty)
    eq_(data['resource'], resource)
    eq_(data['resource_id'], resource_id)


def task_setdata_resource_conversion(resource, id, class_):
    """A Task should convert a resource/resource_id in the data to a Resource"""
    note = Task()
    data = {
        'resource': resource,
        'resource_id': id
    }
    _data = note.format_data_set(data)
    assert isinstance(_data['resource'], class_)


def task_getdata_resource_conversion(instance, resource, resource_id):
    note = Task()
    dirty = {
        'resource': instance
    }
    data = note.format_data_get(dirty)
    eq_(data['resource'], resource)
    eq_(data['resource_id'], resource_id)


def test_note_set_resource_conversion():
    """When calling set_data(), a Note should convert a resource (basestring) and resource_id (int) into a Resource (object)"""
    for resource, class_ in RESOURCE_SET_CONVERSION.iteritems():
        for id in range(0, 5):
            yield note_setdata_resource_conversion, resource, id, class_


def test_note_getdata_resource_conversion():
    """When calling format_data_get(), a Note should convert a Resource (object) into a resource (basestring) and resource_id (int)"""
    for resource, class_ in RESOURCE_SET_CONVERSION.iteritems():
        for id in range(0, 5):
            yield note_getdata_resource_conversion, class_(id), resource, id


def test_task_set_resource_conversion():
    """When calling set_data(), a Note should convert a resource (basestring) and resource_id (int) into a Resource (object)"""
    for resource, class_ in RESOURCE_SET_CONVERSION.iteritems():
        for id in range(0, 5):
            yield task_setdata_resource_conversion, resource, id, class_


def test_task_getdata_resource_conversion():
    """When calling format_data_get(), a Note should convert a Resource (object) into a resource (basestring) and resource_id (int)"""
    for resource, class_ in RESOURCE_SET_CONVERSION.iteritems():
        for id in range(0, 5):
            yield task_getdata_resource_conversion, class_(id), resource, id


"""
v2 Resources should properly wrap the return from format_data_get in 'data'
"""

