__author__ = 'Clayton Daley'

from nose.tools import assert_raises, eq_
from v2.resource import Person, Contact, Organization, Deal, Lead, Note, Tag


def construct_typeerror(class_, i):
    assert_raises(TypeError, class_, i)


def construct_eq(class_, i):
    resource = class_(i)
    eq_(resource.id, i)


def test_generator_contact():
    # Contact throws TypeError on None, telling user to use Person or Organization
    yield construct_typeerror, Contact, None
    # Contact works on valid integers since a user could have an ambiguous contact needing get()
    for i in range(0, 5):
        yield construct_eq, Contact, i
    # Contact throws TypeError on anything but an int
    yield construct_typeerror, Contact, '1'
    yield construct_typeerror, Contact, 'string'


def generator_standard(class_):
    # Standard Classes work on None so you can create() a new instance
    yield construct_typeerror, Contact, None
    # Standard Classes work on valid integers so you can get() an existing record
    for i in range(0, 5):
        yield construct_eq, Contact, i
    # Standard Classes throw TypeError on anything but an int
    yield construct_typeerror, Contact, '1'
    yield construct_typeerror, Contact, 'string'

STANDARD_RESOURCES = [Person, Organization, Deal, Lead, Note, Tag]


def test_generator_standard():
    for resource in STANDARD_RESOURCES:
        for test in generator_standard(resource):
            yield test

