#!/usr/bin/env python
"""Test the functionality of implemented Resources"""

import logging
logger = logging.getLogger(__name__)

from datetime import datetime
from v2.resource import Person, Contact, Organization, Deal, Lead, Note, Tag, Account, Address, LossReason, Task, \
    DealContact, Pipeline, Source, Stage, User
from v2.collection import ContactSet, PersonSet, OrganizationSet, DealSet, LeadSet, LossReasonSet, NoteSet, PipelineSet, \
    SourceSet, StageSet, TagSet, TaskSet, UserSet

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


RESOURCES = [Account, Address, DealContact, Contact, Person, Organization, Deal, Lead, LossReason, Note, Pipeline,
             Source, Stage, Tag, Task, User]
COLLECTIONS = [ContactSet, PersonSet, OrganizationSet, DealSet, LeadSet, LossReasonSet, NoteSet, PipelineSet, SourceSet,
               StageSet, TagSet, TaskSet, UserSet]


def mock_collection(class_):
    return class_()


def mock_resource(class_):
    if class_ is Contact:
        return class_(11)
    elif class_ is DealContact:
        return class_(Deal(27), Contact(35))
    else:
        return class_()


SAMPLES = {
    bool: [True, False],
    int: [75, 63],
    basestring: ['old_string', u'unicode_string'],
    list: [[], ['1', 'a', 1]],
    dict: [{'keyed': 'values'}, {0: 'values'}],
    datetime: [datetime.now(), datetime(2015, 4, 24, 15, 46, 23)],
}
# Required for positive tests on constraints that match Resources
SAMPLES.update({r: [mock_resource(r)] for r in RESOURCES})
# Provides helpful negative tests
SAMPLES.update({c: [mock_collection(c)] for c in COLLECTIONS})