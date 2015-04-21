#!/usr/bin/env python
"""Implements Collections for BaseCRM's v2 API"""

import logging
logger = logging.getLogger(__name__)

from prototype import Collection
from v2.resource import Organization, Person, Deal, Lead, LossReason, Note, Tag, Contact, DealContact, Pipeline, Source, \
    Stage, User, Task

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


class AddressFilter(Collection):
    FILTERS = {
        'city': basestring,
        'postal_code': basestring,
        'country': basestring,
    }

    def format_data_set(self):
        data = super(AddressFilter, self).format_data_set()
        if 'city' in data:
            data['city'] = str(data['city']).lower()
        if 'region' in data:
            data['region'] = str(data['region']).lower()
        if 'country' in data:
            data['country'] = str(data['country']).lower()
        return data


class ContactSet(Collection):
    _PATH = Contact._PATH
    FILTERS = {
        'ids': list,
        'is_organization': bool,
        'contact_id': int,
        'name': basestring,
        'first_name': basestring,
        'last_name': basestring,
        'email': basestring,
        'address': AddressFilter,
    }
    ORDERS = [
        'name',
        'first_name',
        'last_name',
        'updated_at',
        'created_at'
    ]

    def format_page(self, data):
        # This tweak is unique to Contact since it doesn't have a valid _ITEM
        if self.__class__.__name__ != "ContactSet":
            return super(ContactSet, self).set_data(data)

        page = list()
        for record in data:
            if record['data']['is_organization']:
                entity = Organization()
            else:
                entity = Person()
            entity.set_data(record['data'])
            page.append(entity)
        return page


class PersonSet(ContactSet):
    # Persons have a fixed is_organization
    FILTERS = {k: ContactSet.FILTERS[k] for k in ContactSet.FILTERS if k != 'is_organization'}
    _ITEM = Person

    def format_data_set(self):
        data = super(PersonSet, self).format_data_set()
        data['is_organization'] = False
        return data


class OrganizationSet(ContactSet):
    # Organizations cannot have a parent organization (contact_id) and have a fixed is_organization
    FILTERS = {k: ContactSet.FILTERS[k] for k in ContactSet.FILTERS if k not in ['is_organization', 'contact_id']}
    _ITEM = Organization

    def format_data_set(self):
        data = super(OrganizationSet, self).format_data_set()
        data['is_organization'] = True
        return data


class DealSet(Collection):
    _ITEM = Deal
    FILTERS = {
        'ids': list,
        'creator_id': int,
        'owner_id': int,
        'contact_id': int,
        'organization_id': int,
        'hot': bool,
        'stage_id': int,
        'source_id': int,
    }
    ORDERS = [
        'id',
        'value',
        'name',
        'created_at',
        'updated_at',
    ]

    def format_data_set(self):
        data = super(DealSet, self).format_data_set()
        if 'city' in data:
            data['city'] = str(data['city']).lower()
        if 'region' in data:
            data['region'] = str(data['region']).lower()
        if 'country' in data:
            data['country'] = str(data['country']).lower()


class DealContactSet(Collection):
    """
    DealContactSet provides a list of Contacts (Persons or Organizations) associated with a particular Deal
    """
    # order_by parameter not supported
    ORDERS = []
    # deal is identified in URL, no additional filters are available
    FILTERS = {}
    _PATH = "associated_contacts"

    @property
    def PATH(self, debug):
        """Need to overload path since associated_contacts are nested under a specific deal"""
        return self.data.deal.PATH(debug) + "/%s" % self._PATH

    def __init__(self, deal):
        if deal.id is None:
            raise ReferenceError("Deal must have an id or associated Contacts cannot be requested.")
        self.deal = deal
        super(DealContactSet, self).__init__()

    def format_page(self, data):
        # Reset local data
        page = list()
        for record in data:
            item = DealContact(self.deal, Contact(record['data']['contact_id']))
            item.role = record['data']['role']
            page.append(item)
        return page

    def format_data_set(self):
        if self.id is None:
            raise ReferenceError('')


class LeadSet(Collection):
    _ITEM = Lead
    FILTERS = {
        'ids': list,
        'creator_id': int,
        'owner_id': int,
        'first_name': basestring,
        'last_name': basestring,
        'organization_name': basestring,
        'status': basestring,
        'address': AddressFilter,
    }
    ORDERS = [
        'first_name',
        'last_name',
        'organization_name',
        'updated_at',
        'created_at'
    ]

    def format_data_set(self):
        data = super(LeadSet, self).format_data_set()
        if 'city' in data:
            data['city'] = str(data['city']).lower()
        if 'region' in data:
            data['region'] = str(data['region']).lower()
        if 'country' in data:
            data['country'] = str(data['country']).lower()


class LossReasonSet(Collection):
    _ITEM = LossReason
    FILTERS = {
        'ids': list,
        'name': basestring,
    }
    ORDERS = [
        'id',
        'name',
        'updated_at',
        'created_at'
    ]


class NoteSet(Collection):
    _ITEM = Note
    FILTERS = {
        # includes: basestring,
        'ids': list,
        'creator_id': int,
        'q': basestring,
        'name': basestring,
        'resource_type': {
            'type': basestring,
            'in': _ITEM.RESOURCE_TYPES
        },
        'resource_id': int,
    }
    ORDERS = [
        'name',
        'updated_at',
        'created_at'
    ]


class PipelineSet(Collection):
    _ITEM = Pipeline
    FILTERS = {
        'ids': list,
        'name': basestring,
    }
    ORDERS = [
        'id',
        'name',
    ]


class SourceSet(Collection):
    _ITEM = Source
    FILTERS = {
        'ids': list,
        'name': basestring,
    }
    ORDERS = [
        'id',
        'name',
    ]


class StageSet(Collection):
    _ITEM = Stage
    FILTERS = {
        'ids': list,
        'name': basestring,
        'pipeline_id': int,
        'active': bool,
    }
    ORDERS = [
        'id',
        'name',
        'category',
        'position',
        'likelihood',
        'pipeline_id',
    ]


class TagSet(Collection):
    _ITEM = Tag
    FILTERS = {
        'ids': list,
        'creator_id': int,
        'name': basestring,
        'resource_type': {
            'type': basestring,
            'in': _ITEM.RESOURCE_TYPES
        },
    }
    ORDERS = [
        'name',
        'updated_at',
        'created_at'
    ]


class TaskSet(Collection):
    _ITEM = Task
    # The search offers this additional type declaration
    TYPES = [
        'floating',
        'related'
    ]
    FILTERS = {
        'ids': list,
        'creator_id': int,
        'owner_id': int,
        'q': basestring,
        'type': {
            'type': basestring,
            'in': TYPES
        },
        'resource_type': {
            'type': basestring,
            'in': _ITEM.RESOURCE_TYPES
        },
        'resource_id': int,
        'completed': bool,
        'overdue': bool,
        'remind': bool,
    }
    ORDERS = [
        'resource_type',
        'completed_at',
        'due_date',
        'created_at',
        'updated_at',
    ]


class UserSet(Collection):
    _ITEM = User
    FILTERS = {
        'ids': list,
        'name': basestring,
        'email': basestring,
        'status': {
            'type': basestring,
            'in': _ITEM.STATUS
        },
        'role': {
            'type': basestring,
            'in': _ITEM.ROLE
        },
        'confirmed': bool,
    }
    ORDERS = [
        'ids',
        'name',
        'updated_at',
        'created_at'
    ]