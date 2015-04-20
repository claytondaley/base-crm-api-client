__author__ = 'Clayton Daley'

import logging
logger = logging.getLogger(__name__)

from copy import deepcopy
from prototypes import Resource


def _key_coded_dict(d):
    new_dict = dict()
    for k, v in d.iteritems():
        if isinstance(d, dict):
            for k2, v2 in v.iteritems():
                new_dict['%s[%s]' % k, k2] = v2
        else:
            new_dict[k] = v
    return new_dict


class Account(Resource):
    _PATH = "accounts"
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
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
        self.__dict__['data']['id'] = 'self'



class Address(Resource):
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
        'line1': basestring,
        'city': basestring,
        'postal_code': basestring,
        'state': basestring,
        'country': basestring,
    }


class Contact(Resource):
    _PATH = "contacts"
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
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
        for k, v in data.items():
            if k == 'address':
                address = Address()
                address.set_data(v)
                data[k] = address
        if data['is_organization']:
            self.__class__ = Organization
        else:
            self.__class__ = Person
        return data  # data is mutable, but this simplifies chaining and inline assignment


class Person(Contact):
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
        '_id': int,
        '_creator_id': int,
        'owner_id': int,
        '_is_organization': bool,
        'contact_id': int,
        'name': basestring,
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
        self.dirty['is_organization'] = False

    def params(self):
        params = super(Person, self).params()
        # Check business rules
        # If ID is not None, assume an update
        if self.id is None:
            # Otherwise, both first_name and last_name are required for a Person
            if 'first_name' not in params or params['first_name'] is None or \
                    'last_name' not in params or params['last_name'] is None:
                raise ValueError("first_name and last_name must be set unless an id is provided")
        # Other checks for the type of action (get, post, put, delete) are made in client
        return params


class Organization(Contact):
    PROPERTIES = Contact.PROPERTIES

    def __init__(self, entity_id=None):
        super(Organization, self).__init__(entity_id)
        self.dirty['is_organization'] = True

    def params(self):
        params = super(Person, self).params()
        # Check business rules
        # If ID is not None, assume an update
        if self.id is None:
            # Otherwise, name is required for an Organization
            if 'name' not in params or params['name'] is None:
                raise ValueError("name must be set unless an id is provided")
        # Other checks for the type of action (get, post, put, delete) are made in client
        return params


class Deal(Resource):
    _PATH = "deals"
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
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
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
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
    def URL(self, debug):
        return self.data.deal.PATH(debug) + "/%s/%s" % (self.API_VERSION, self._PATH, self.id)

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
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
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

    def set_data(self, data):
        local = self.__dict__
        local['data'] = dict()
        for k, v in data.items():
            if k == 'address':
                address = Address()
                address.set_data(v)
                local[k] = address
            else:
                local[k] = v
        local['loaded'] = True


class LossReason(Resource):
    _PATH = "loss_reasons"
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
        '_id': int,
        '_creator_id': int,
        'name': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Note(Resource):
    _PATH = "notes"
    RESOURCE_TYPES = [
        'lead',
        'contact',
        'deal',
    ]
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
        '_id': int,
        '_creator_id': int,
        'resource_type': {
            'type': basestring,
            'in': RESOURCE_TYPES
        },
        'resource_id': int,
        'content': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Pipeline(Resource):
    _PATH = "pipelines"
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
        '_id': int,
        '_name': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Source(Resource):
    _PATH = "sources"
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
        '_id': int,
        '_creator_id': int,
        'name': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


class Stage(Resource):
    _PATH = "stages"
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
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
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
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
    RESOURCE_TYPES = [
        'lead',
        'contact',
        'deal',
    ]
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
        '_id': int,
        '_creator_id': int,
        'owner_id': int,
        'resource_type': {
            'type': basestring,
            'in': RESOURCE_TYPES
        },
        'resource_id': int,
        'completed': bool,
        '_completed_at': basestring,
        'due_date': basestring,
        '_overdue': bool,
        'remind_at': basestring,
        'content': basestring,
        '_created_at': basestring,
        '_updated_at': basestring,
    }


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
    PROPERTIES = {
        """
        Read-only attributes are proceeded by an underscore
        """
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


