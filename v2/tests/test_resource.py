
__author__ = 'Clayton Daley'

from nose.tools import assert_raises, eq_
from pprint import pprint
from v2.resource import Person, Contact, Organization, Deal, Lead, Note, Tag, Account, Address, LossReason

"""
CONSTRUCTOR BEHAVIOR

This section verifies that constructors follow the standard pattern unless otherwise specified

"""


def construct_typeerror(class_, i):
    assert_raises(TypeError, class_, i)


def construct_eq(class_, i):
    resource = class_(i)
    eq_(resource.id, i)

STANDARD_RESOURCES = [Person, Organization, Deal, Lead, Note, Tag]


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
    for resource in STANDARD_RESOURCES:
        for test in generator_standard(resource):
            yield test


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
Attribute behavior
"""


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


RESOURCES = [
    Account, Address, Person, Organization, Deal, Lead, LossReason, Note, Tag,
    # Pipeline, Source, Stage, Task, User  # special behavior for Contact
]


def test_resource_setattr():
    for class_ in RESOURCES:
        resource = class_()
        for attrib, type in resource.PROPERTIES.iteritems():
            # readonly properties produce KeyError when set
            if attrib[0] == '_':
                yield setattr_keyerror, resource, attrib[1:], None
            # other properties may be set
            else:
                if type == int:
                    yield setattr_eq, resource, attrib, 1
                elif type == basestring:
                    yield setattr_eq, resource, attrib, 'test_string'
                else:
                    print "Missing test for %s" % pprint(type)