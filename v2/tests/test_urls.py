from nose.tools import eq_, assert_raises
from v2.collection import ContactSet, PersonSet, OrganizationSet, DealSet, LeadSet, NoteSet
from v2.resource import Contact, Person, Deal, Lead, Address, Organization, Note, Account, Tag, LossReason, Source, \
    Stage, User, Pipeline, Task

__author__ = 'Clayton Daley'


PASSING_URL_TESTS = [
    #Class              KWARGS              DEBUG       URL
    [Account,           dict(),             True,       'https://api.sandbox.getbase.com/v2/accounts/self'],
    [Account,           dict(),             False,      'https://api.getbase.com/v2/accounts/self'],

    [ContactSet,        dict(),             True,       'https://api.sandbox.getbase.com/v2/contacts'],
    [ContactSet,        dict(),             False,      'https://api.getbase.com/v2/contacts'],
    [Contact,           {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/contacts/1'],
    [Contact,           {'entity_id': 1},   False,      'https://api.getbase.com/v2/contacts/1'],
    [Contact,           {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/contacts/50'],
    [Contact,           {'entity_id': 50},  False,      'https://api.getbase.com/v2/contacts/50'],

    [PersonSet,         dict(),             True,       'https://api.sandbox.getbase.com/v2/contacts'],
    [PersonSet,         dict(),             False,      'https://api.getbase.com/v2/contacts'],
    [Person,            dict(),             True,       'https://api.sandbox.getbase.com/v2/contacts'],
    [Person,            dict(),             False,      'https://api.getbase.com/v2/contacts'],
    [Person,            {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/contacts/1'],
    [Person,            {'entity_id': 1},   False,      'https://api.getbase.com/v2/contacts/1'],
    [Person,            {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/contacts/50'],
    [Person,            {'entity_id': 50},  False,      'https://api.getbase.com/v2/contacts/50'],

    [OrganizationSet,   dict(),             True,       'https://api.sandbox.getbase.com/v2/contacts'],
    [OrganizationSet,   dict(),             False,      'https://api.getbase.com/v2/contacts'],
    [Organization,      dict(),             True,       'https://api.sandbox.getbase.com/v2/contacts'],
    [Organization,      dict(),             False,      'https://api.getbase.com/v2/contacts'],
    [Organization,      {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/contacts/1'],
    [Organization,      {'entity_id': 1},   False,      'https://api.getbase.com/v2/contacts/1'],
    [Organization,      {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/contacts/50'],
    [Organization,      {'entity_id': 50},  False,      'https://api.getbase.com/v2/contacts/50'],

    [DealSet,           dict(),             True,       'https://api.sandbox.getbase.com/v2/deals'],
    [DealSet,           dict(),             False,      'https://api.getbase.com/v2/deals'],
    [Deal,              dict(),             True,       'https://api.sandbox.getbase.com/v2/deals'],
    [Deal,              dict(),             False,      'https://api.getbase.com/v2/deals'],
    [Deal,              {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/deals/1'],
    [Deal,              {'entity_id': 1},   False,      'https://api.getbase.com/v2/deals/1'],
    [Deal,              {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/deals/50'],
    [Deal,              {'entity_id': 50},  False,      'https://api.getbase.com/v2/deals/50'],
    [Deal,              dict(),             False,      'https://api.getbase.com/v2/deals'],

    [LeadSet,           dict(),             True,       'https://api.sandbox.getbase.com/v2/leads'],
    [LeadSet,           dict(),             False,      'https://api.getbase.com/v2/leads'],
    [Lead,              dict(),             True,       'https://api.sandbox.getbase.com/v2/leads'],
    [Lead,              dict(),             False,      'https://api.getbase.com/v2/leads'],
    [Lead,              {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/leads/1'],
    [Lead,              {'entity_id': 1},   False,      'https://api.getbase.com/v2/leads/1'],
    [Lead,              {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/leads/50'],
    [Lead,              {'entity_id': 50},  False,      'https://api.getbase.com/v2/leads/50'],

    [LossReason,        dict(),             True,       'https://api.sandbox.getbase.com/v2/loss_reasons'],
    [LossReason,        dict(),             False,      'https://api.getbase.com/v2/loss_reasons'],
    [LossReason,        {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/loss_reasons/1'],
    [LossReason,        {'entity_id': 1},   False,      'https://api.getbase.com/v2/loss_reasons/1'],
    [LossReason,        {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/loss_reasons/50'],
    [LossReason,        {'entity_id': 50},  False,      'https://api.getbase.com/v2/loss_reasons/50'],

    [NoteSet,           dict(),             True,       'https://api.sandbox.getbase.com/v2/leads'],
    [NoteSet,           dict(),             False,      'https://api.getbase.com/v2/leads'],
    [Note,              dict(),             True,       'https://api.sandbox.getbase.com/v2/notes'],
    [Note,              dict(),             False,      'https://api.getbase.com/v2/notes'],
    [Note,              {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/notes/1'],
    [Note,              {'entity_id': 1},   False,      'https://api.getbase.com/v2/notes/1'],
    [Note,              {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/notes/50'],
    [Note,              {'entity_id': 50},  False,      'https://api.getbase.com/v2/notes/50'],

    [Pipeline,          dict(),             True,       'https://api.sandbox.getbase.com/v2/pipelines'],
    [Pipeline,          dict(),             False,      'https://api.getbase.com/v2/pipelines'],
    [Pipeline,          {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/pipelines/1'],
    [Pipeline,          {'entity_id': 1},   False,      'https://api.getbase.com/v2/pipelines/1'],
    [Pipeline,          {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/pipelines/50'],
    [Pipeline,          {'entity_id': 50},  False,      'https://api.getbase.com/v2/pipelines/50'],

    [Source,            dict(),             True,       'https://api.sandbox.getbase.com/v2/sources'],
    [Source,            dict(),             False,      'https://api.getbase.com/v2/sources'],
    [Source,            {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/sources/1'],
    [Source,            {'entity_id': 1},   False,      'https://api.getbase.com/v2/sources/1'],
    [Source,            {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/sources/50'],
    [Source,            {'entity_id': 50},  False,      'https://api.getbase.com/v2/sources/50'],

    [Stage,             dict(),             True,       'https://api.sandbox.getbase.com/v2/stages'],
    [Stage,             dict(),             False,      'https://api.getbase.com/v2/stages'],
    [Stage,             {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/stages/1'],
    [Stage,             {'entity_id': 1},   False,      'https://api.getbase.com/v2/stages/1'],
    [Stage,             {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/stages/50'],
    [Stage,             {'entity_id': 50},  False,      'https://api.getbase.com/v2/stages/50'],

    [Tag,               dict(),             True,       'https://api.sandbox.getbase.com/v2/tags'],
    [Tag,               dict(),             False,      'https://api.getbase.com/v2/tags'],
    [Tag,               {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/tags/1'],
    [Tag,               {'entity_id': 1},   False,      'https://api.getbase.com/v2/tags/1'],
    [Tag,               {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/tags/50'],
    [Tag,               {'entity_id': 50},  False,      'https://api.getbase.com/v2/tags/50'],

    [Task,              dict(),             True,       'https://api.sandbox.getbase.com/v2/tasks'],
    [Task,              dict(),             False,      'https://api.getbase.com/v2/tasks'],
    [Task,              {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/tasks/1'],
    [Task,              {'entity_id': 1},   False,      'https://api.getbase.com/v2/tasks/1'],
    [Task,              {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/tasks/50'],
    [Task,              {'entity_id': 50},  False,      'https://api.getbase.com/v2/tasks/50'],

    [User,              dict(),             True,       'https://api.sandbox.getbase.com/v2/users'],
    [User,              dict(),             False,      'https://api.getbase.com/v2/users'],
    [User,              {'entity_id': 1},   True,       'https://api.sandbox.getbase.com/v2/users/1'],
    [User,              {'entity_id': 1},   False,      'https://api.getbase.com/v2/users/1'],
    [User,              {'entity_id': 50},  True,       'https://api.sandbox.getbase.com/v2/users/50'],
    [User,              {'entity_id': 50},  False,      'https://api.getbase.com/v2/users/50'],
]


def url_check_eq(class_, kwargs, debug, url):
    """
    For a class_ constructed with kwargs, the URL method (called with the debug as a paramter) should return url
    """
    instance = class_(**kwargs)
    eq_(instance.URL(debug), url)


def test_generator_url_eq():
    """
    Verify that each of the combinations in PASSING_URL_TESTS generates teh expected URL
    """
    for case in PASSING_URL_TESTS:
        yield url_check_eq, case[0], case[1], case[2], case[3]


REFERENCEERROR_URL_TESTS = [
    #Class              KWARGS              DEBUG
    [Address,           {'entity_id': 1},   True],
    [Address,           {'entity_id': 1},   False],
]


def url_check_referenceerror(class_, kwargs, debug):
    """
    The following classes, when constructed using kwargs should raise a ReferenceError when URL is called
    """
    instance = class_(**kwargs)
    assert_raises(ReferenceError, instance.URL, debug)


def test_generator_url_referenceerror():
    """
    Test that the combinations in REFERENCEERROR_URL_TESTS actually generate the expected error
    """
    for case in REFERENCEERROR_URL_TESTS:
        yield url_check_referenceerror, case[0], case[1], case[2]


