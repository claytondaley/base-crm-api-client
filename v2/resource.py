#!/usr/bin/env python
"""Implements Resources for BaseCRM's v2 API"""

import logging
logger = logging.getLogger(__name__)

from prototype import Resource

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


class Account(Resource):
    _PATH = "accounts"
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_name': basestring,
        '_currency': basestring,
        '_time_format': basestring,
        '_timezone': int,
        '_phone': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }

    def __init__(self):
        super(Account, self).__init__()
        # Account only works to load the "ID" /self
        self.__dict__['_data']['id'] = 'self'


class Address(Resource):
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        'line1': basestring,
        'city': basestring,
        'postal_code': basestring,
        'state': basestring,
        'country': basestring,
    }

    def URL(self, debug=False):
        raise ReferenceError("Address has no dedicated REST endpoint. The object is only found in other Entities.")


class Contact(Resource):
    _PATH = "contacts"
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        '_owner_id': int,
        '_is_organization': bool,
        '_contact_id': int,
        '_name': basestring,
        '_first_name': basestring,
        '_last_name': basestring,
        '_customer_status': basestring,
        '_prospect_status': basestring,
        '_title': basestring,
        '_description': basestring,
        '_industry': basestring,
        '_website': basestring,
        '_email': basestring,
        '_phone': basestring,
        '_mobile': basestring,
        '_fax': basestring,
        '_twitter': basestring,
        '_facebook': basestring,
        '_linkedin': basestring,
        '_skype': basestring,
        '_address': Address,
        '_tags': list,
        '_custom_fields': dict,
        '_created_at': basestring,
        '_updated_at': basestring,
    }

    def __init__(self, entity_id=None):
        if self.__class__.__name__ == "Contact" and entity_id is None:
            raise TypeError("Contact should only be created when loading an (ambiguous) id.  For any other purpose, " +
                            "use Person or Organization instead.")
        # If a user has an ambiguous contact, it must be possible to load that contact by ID
        super(Contact, self).__init__(entity_id)

    def set_data(self, data):
        super(Contact, self).set_data(data)
        # Mutate last
        if data['data']['is_organization']:
            object.__setattr__(self, '__class__', Organization)
        else:
            object.__setattr__(self, '__class__', Person)
        return self  # returned for setting and chaining convenience

    def format_data_set(self, data):
        for k, v in data.iteritems():
            if k == 'address':
                address = Address()
                address.set_data({'data': v})  # Nest back in a 'data' key to use default processor
                data[k] = address
        return data  # data is mutable, but this simplifies chaining and inline assignment


class Person(Contact):
    """
    A specialization of the Contact object that assumes is_organization=False and enforces related business rules.
    """
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        'owner_id': int,
        '_is_organization': bool,
        'contact_id': int,
        '_name': basestring,  # API will accept value, but fails to update 'name' from "<First> <Last>"
        'first_name': basestring,
        'last_name': basestring,
        'customer_status': basestring,
        'prospect_status': basestring,
        'title': basestring,
        'description': basestring,
        'industry': basestring,
        'website': basestring,
        'email': basestring,
        'phone': basestring,
        'mobile': basestring,
        'fax': basestring,
        'twitter': basestring,
        'facebook': basestring,
        'linkedin': basestring,
        'skype': basestring,
        'address': Address,
        'tags': list,
        'custom_fields': dict,
        '_created_at': basestring,
        '_updated_at': basestring,
    }

    def __init__(self, entity_id=None):
        super(Person, self).__init__(entity_id)
        self._dirty['is_organization'] = False

    def format_data_get(self):
        data = super(Person, self).format_data_get()
        # Check business rules
        # If ID is not None, assume an update
        if self.id is None:
            # Otherwise, both first_name and last_name are required for a Person
            if 'first_name' not in data or data['first_name'] is None or \
                    'last_name' not in data or data['last_name'] is None:
                raise ValueError("first_name and last_name must be set unless an id is provided")
        # Other checks for the type of action (get, post, put, delete) are made in client
        return data

    def format_data_set(self, data):
        if data['is_organization']:
            raise ValueError('Data for Organization provided to Person')
        super(Person, self).format_data_set(data)


class Organization(Contact):
    """
    A specialization of the Contact object that assumes is_organization=True and enforces related business rules.
    """
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        'owner_id': int,
        '_is_organization': bool,
        'contact_id': int,
        'name': basestring,  # API will accept value, but fails to update 'name' from "<First> <Last>"
        '_first_name': basestring,
        '_last_name': basestring,
        'customer_status': basestring,
        'prospect_status': basestring,
        'title': basestring,
        'description': basestring,
        'industry': basestring,
        'website': basestring,
        'email': basestring,
        'phone': basestring,
        'mobile': basestring,
        'fax': basestring,
        'twitter': basestring,
        'facebook': basestring,
        'linkedin': basestring,
        'skype': basestring,
        'address': Address,
        'tags': list,
        'custom_fields': dict,
        '_created_at': basestring,
        '_updated_at': basestring,
    }

    def __init__(self, entity_id=None):
        super(Organization, self).__init__(entity_id)
        self._dirty['is_organization'] = True

    def format_data_get(self, dirty):
        data = super(Person, self).format_data_get(dirty)
        # Check business rules
        # If ID is not None, assume an update
        if self.id is None:
            # Otherwise, name is required for an Organization
            if 'name' not in data or data['name'] is None:
                raise ValueError("name must be set unless an id is provided")
        # Other checks for the type of action (get, post, put, delete) are made in client
        return data

    def format_data_set(self, data):
        if not data['is_organization']:
            raise ValueError('Data for Person provided to Organization')
        super(Organization, self).format_data_set(data)


class Deal(Resource):
    _PATH = "deals"
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        'owner_id': int,
        'contact_id': int,
        'name': basestring,  # Write only (!?)
        'value': int,
        'currency': basestring,
        'hot': bool,
        'stage_id': int,
        'source_id': int,
        'loss_reason_id': int,
        '_dropbox_email': basestring,
        '_organization_id': int,
        'tags': list,
        'custom_fields': dict,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class DealContact(Resource):
    _PATH = "associated_contacts"
    ROLES = [
        'involved'
    ]
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_deal': Deal,
        '_contact': Contact,
        'role': {
            'type': basestring,
            'in': ROLES,
        },
        '_created_at': basestring,
        '_updated_at': basestring,
    }
    _PATH = "associated_contacts"

    @property
    def URL(self, debug=False):
        return self._data.deal.PATH(debug) + "/%s/%s" % (self.API_VERSION, self._PATH, self.id)

    def __init__(self, deal, contact):
        if deal.id is None:
            raise ReferenceError("Deal must have an id before Contacts can be associated.  Please use create() to " +
                                 "get an ID for the Deal")
        if contact.id is None:
            raise ReferenceError("Contact must have an id before it can be associated with a Deal.  Please use " +
                                 "create() to get an ID for the Contact")
        super(DealContact, self).__init__(contact.id)


class Lead(Resource):
    _PATH = "leads"
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        'owner_id': int,
        'first_name': basestring,
        'last_name': basestring,
        'organization_name': basestring,
        'status': basestring,
        'title': basestring,
        'description': basestring,
        'industry': basestring,
        'website': basestring,
        'email': basestring,
        'phone': basestring,
        'mobile': basestring,
        'fax': basestring,
        'twitter': basestring,
        'facebook': basestring,
        'linkedin': basestring,
        'skype': basestring,
        'address': Address,
        'tags': list,
        'custom_fields': dict,
        '_created_at': basestring,
        '_updated_at': basestring,
    }

    def format_data_set(self, data):
        for k, v in data.iteritems():
            if k == 'address':
                address = Address()
                address.set_data({'data': v})
                data[k] = address


class LossReason(Resource):
    _PATH = "loss_reasons"
    PROPERTIES = {
        """
        Read-only attributes are preceded by an underscore
        """
        '_id': int,
        '_creator_id': int,
        'name': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Note(Resource):
    _PATH = "notes"
    RESOURCE_TYPES = {
        'lead': Lead,
        'contact': Contact,
        'deal': Deal,
    }
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        'resource': {
            'type': [
                Contact,
                Deal,
                Lead,
            ]
        },
        'content': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }

    def format_data_set(self, data):
        """
        Input is:
        ...
        'resource_type': {
            'type': basestring,
            'in': RESOURCE_TYPES
        },
        'resource_id': int,
        ...
        """
        class_ = self.RESOURCE_TYPES[data['resource']]
        data['resource'] = class_(data['resource_id'])
        del data['resource_id']
        return data

    def format_data_get(self, dirty):
        data = super(Note, self).format_data_get(dirty)
        if 'resource' in data:
            data['resource_id'] = data['resource'].id
            data['resource'] = data['resource'].__class__.__name__.lower()
        return data


class Pipeline(Resource):
    _PATH = "pipelines"
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_name': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Source(Resource):
    _PATH = "sources"
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        'name': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Stage(Resource):
    _PATH = "stages"
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_name': basestring,
        '_category': basestring,
        '_active': bool,
        '_position': int,
        '_likelihood': int,
        '_pipeline_id': int,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Tag(Resource):
    _PATH = "tags"
    RESOURCE_TYPES = [
        'lead',
        'contact',
        'deal',
    ]
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        'name': basestring,
        'resource_type': {
            'type': basestring,
            'in': RESOURCE_TYPES
        },
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Task(Resource):
    _PATH = "tasks"
    RESOURCE_TYPES = {
        'lead': Lead,
        'contact': Contact,
        'deal': Deal,
    }
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_creator_id': int,
        'owner_id': int,
        'resource': {
            'type': [
                Contact,
                Deal,
                Lead,
            ]
        },
        'completed': bool,
        '_completed_at': basestring,
        'due_date': basestring,
        '_overdue': bool,
        'remind_at': basestring,
        'content': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }

    def format_data_set(self, data):
        """
        Input is:
        ...
        'resource_type': {
            'type': basestring,
            'in': RESOURCE_TYPES
        },
        'resource_id': int,
        ...
        """
        class_ = self.RESOURCE_TYPES[data['resource']]
        data['resource'] = class_(data['resource_id'])
        del data['resource_id']
        return data

    def format_data_get(self, dirty):
        data = super(Task, self).format_data_get(dirty)
        if 'resource' in data:
            data['resource_id'] = data['resource'].id
            data['resource'] = data['resource'].__class__.__name__.lower()
        return data


class User(Resource):
    _PATH = "users"
    STATUS = [
        'active',
        'inactive',
    ]
    ROLE = [
        'user',
        'admin',
    ]
    """
    Read-only attributes are preceded by an underscore
    """
    PROPERTIES = {
        '_id': int,
        '_name': basestring,
        '_email': basestring,
        '_status': {
            'type': basestring,
            'in': STATUS
        },
        '_role': {
            'type': basestring,
            'in': ROLE
        },
        '_confirmed': bool,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


