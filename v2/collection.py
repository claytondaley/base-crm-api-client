__author__ = 'Clayton Daley'

from prototypes import Collection
from v2.resource import Organization, Person, Deal, Lead, LossReason, Note, Tag, Contact, DealContact


class AddressFilter(Collection):
    FILTERS = {
        'city': basestring,
        'postal_code': basestring,
        'country': basestring,
    }

    def params(self):
        params = super(AddressFilter, self).params()
        if 'city' in params:
            params['city'] = str(params['city']).lower()
        if 'region' in params:
            params['region'] = str(params['region']).lower()
        if 'country' in params:
            params['country'] = str(params['country']).lower()
        return params


class ContactSet(Collection):
    _PATH = "contacts"
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

    def params(self):
        params = super(PersonSet, self).params()
        params['is_organization'] = False
        return params


class OrganizationSet(ContactSet):
    # Organizations cannot have a parent organization (contact_id) and have a fixed is_organization
    FILTERS = {k: ContactSet.FILTERS[k] for k in ContactSet.FILTERS if k not in ['is_organization', 'contact_id']}
    _ITEM = Organization

    def params(self):
        params = super(OrganizationSet, self).params()
        params['is_organization'] = True
        return params


class DealSet(Collection):
    _ITEM = Deal
    _PATH = "deals"
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

    def params(self):
        params = super(DealSet, self).params()
        if 'city' in params:
            params['city'] = str(params['city']).lower()
        if 'region' in params:
            params['region'] = str(params['region']).lower()
        if 'country' in params:
            params['country'] = str(params['country']).lower()


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

    def params(self):
        if self.id is None:
            raise ReferenceError('')


class LeadSet(Collection):
    _ITEM = Lead
    _PATH = "leads"
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

    def params(self):
        params = super(LeadSet, self).params()
        if 'city' in params:
            params['city'] = str(params['city']).lower()
        if 'region' in params:
            params['region'] = str(params['region']).lower()
        if 'country' in params:
            params['country'] = str(params['country']).lower()


class LossReasonSet(Collection):
    _ITEM = LossReason
    _PATH = "leads"
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
    _PATH = "leads"
    FILTERS = {
        # 'includes',
        'ids': list,
        'creator_id': basestring,
        'q': basestring,
        'resource_type': {
            'type': basestring,
            'in': Tag.RESOURCE_TYPES
        },
        'resource_id': int,
    }
    ORDERS = [
        'resource_type',
        'updated_at',
        'created_at'
    ]


class NoteSet(Collection):
    _ITEM = Tag
    _PATH = "leads"
    FILTERS = {
        'ids': list,
        'creator_id': basestring,
        'name': basestring,
        'resource_type': {
            'type': basestring,
            'in': Tag.RESOURCE_TYPES
        },
    }
    ORDERS = [
        'name',
        'updated_at',
        'created_at'
    ]
