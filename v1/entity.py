#!/usr/bin/env python
"""Implements Entities for BaseCRM's v1 API"""

import logging
logger = logging.getLogger(__name__)

from copy import deepcopy
from prototype import ResourceV1, CollectionV1, _key_coded_dict

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


"""
V1 API CHARACTERISTICS

Due to a relatively low level of standardization among BaseCRM resources, this table has been accumulated

FIELD               PAGING                          RESPONSE STRUCTURE
Name (interface)    0               1               Items Key   Success Field   Fields
                                                    (1)         w/ Object (1)
Contacts (API)      duplicates 1    beginning       False       False           38
Deals (API)         404             beginning       False       False           28
Leads (API)         beginning       2nd page        True        True            14
Sources (API)       N/A             N/A             False       False           6

Contacts (search)   beginning       2nd page        True        False           17 (2)
Deals (search)      duplicates 1    beginning       True        True            28
Leads (search)      beginning       2nd page        True        True            14

Tags                duplicates 1    beginning       False       False           3
Notes               duplicates 1    beginning       False       False           10
Feed                (3)             (3)             True        True            8 (4)
Tasks               duplicates 1    beginning       False       False           18
Emails              TBD             TBD

(1) Some calls return a simple list of items (indicated in the table by 'False').  Others (indicated in the table by
True) return a dict, nesting the list of items under an 'items' key.

(2) While the search response for Leads and Deals returns the same fields as the get() calls, note that the search
interface for contacts returns a shorter (17 record) response.

(3) While the feed is paged, it does not use the standard page= interface. Instead, the page is managed through the
timestamp= parameter.  The first page is obtained by sending "?timestamp=null".  The timestamp for subsequent pages is
included in the metadata of the previous page.

(4) These records are nested one deeper than standard responses (i.e. response['items'][0]['feed_items']['attributes'] )
"""


class Contact(ResourceV1):
    RESOURCE = 'crm'
    API_VERSION = 1
    _PATH = 'contacts'
    DATA_PARENT_KEY = 'contact'
    PROPERTIES = {
        """
        Read-only attributes are preceded by an underscore
        """
        # Commented items are not listed as valid PUT/POST variables
        # Private items are not listed, but are almost certainly not allowed
        '_id': int,
        #'creator_id': int,
        #'account_id': int,
        #'user_id': int,
        #'sales_account': int,
        'name': basestring,
        'last_name': basestring,
        'first_name': basestring,
        'is_organisation': bool,
        #'is_sales_account': bool,
        #'organisation': ResourceV1,  # Should be Organisation once this is specified
        #'organisation_name': basestring,
        #'root_entity_id': int,
        #'root_entity_name': basestring,
        #'prospect_status': basestring,
        'contact_id': int,  # For Person, parent organization
        'email': basestring,
        'phone': basestring,
        'mobile': basestring,
        'twitter': basestring,
        #'skype': basestring,
        #'facebook': basestring,
        #'linkedin': basestring,
        #'linkedin_display': basestring,
        'address': basestring,
        'city': basestring,
        #'region': basestring,  # State
        'country': basestring,
        #'zip': basestring,
        'title': basestring,
        'description': basestring,
        'website': basestring,
        'fax': basestring,
        #'_tags_joined_by_comma': basestring,
        'tag_list': basestring,  # different name used for PUT
        'private': bool,
        #'custom_fields': dict,
        #'customer_status': bool,
        '_created_at': basestring,
        '_updated_at': basestring,
        '_version': int,
    }

    def set_data(self, data):
        super(Contact, self).set_data(data)

    def format_data_set(self, data):
        # Return a page containing API data processed into Resources and Collections
        if 'organisation' in data:
            organisation = Contact()
            organisation.set_data(data['organisation'])
            data['organisation'] = organisation
        # Object is mutable, but return for simple chaining and setting
        return data


class ContactSet(CollectionV1):
    _ITEM = Contact
    RESOURCE = 'crm'
    API_VERSION = 1
    _PATH = Contact._PATH
    RESPONSE_KEY = Contact.DATA_PARENT_KEY
    FILTERS = {
        'user_id',
        'city',  # All lower
        'region',  # All lower
        'zip',  # NOT zip_code as listed in aggregate
        'country',  # All lower
        'tag_ids',  # Comma (%2C) separated in URL
        'tags',  # All lower; Comma (%2C) separated in URL
    }
    ORDERS = [
        # Verified not available: organisation_name, mobile, overdue_tasks, phone, unread_emails
        # Included in return list:
        'last_name',
        'first_name',
        'user_id',
        'account_id',
        'title',
        'created_at',
        'is_sales_account',
        'id',
        'is_organisation',
        'email',
        'name',
        # In sort_value if submitted, otherwise not returned:
        'last_activity',
        'calls_to_action,first',
        'calls_to_action,last'
    ]

    def format_data_set(self):
        data = deepcopy(self.filters)
        if 'city' in data:
            data['city'] = str(data['city']).lower()
        if 'region' in data:
            data['region'] = str(data['region']).lower()
        if 'country' in data:
            data['country'] = str(data['country']).lower()
        if 'tags' in data:
            data['tags'] = str(','.join(data['tags'])).lower()
        return _key_coded_dict({self.RESPONSE_KEY: data})


class Lead(ResourceV1):
    API_VERSION = 1
    PATH = "lead"
    PROPERTIES = [
        'lead_id',
        'last_name',
        'company_name',
        'first_name',
        'email',
        'phone',
        'mobile',
        'twitter',
        'skype',
        'facebook',
        'linkedin',
        'street',
        'city',
        'region',
        'zip',
        'country',
        'title',
        'description',
        # Valid for contacts, check for leads
        #        'industry',
        #        'website',
        #        'fax',
        #        'tag_list',
        #        'private',
    ]

    def format_data_get(self):
        pass


class LeadSet(CollectionV1):
    API_VERSION = 1
    _PATH = "lead"
    FILTERS = {
        'tag_ids',
        'owner_id',
        'status_id',
    }
    ORDERS = [
        'account_id',
        'added_on',
        'company_name',
        'created_at',
        'first_name',
        'id',
        'last_activity_date',
        'last_activity',  # Appears to be alias of last_activity_date
        'last_name',
        'owner_id',
        'state',
        'status_id',
        'title',
        #'tag_ids', # Accepted by API but non-functional
        #'tags', # Accepted by API but non-functional
        'user_id',
    ]

    def format_data_set(self):
        data = deepcopy(self.filters)
        if 'city' in data:
            data['city'] = str(data['city']).lower()
        if 'region' in data:
            data['region'] = str(data['region']).lower()
        if 'country' in data:
            data['country'] = str(data['country']).lower()


class Deal(ResourceV1):
    API_VERSION = 1
    PATH = "deal"
    PROPERTIES = [
        'name',
        'entity_id',
        'scope',
        'hot',
        'deal_tags',
        'contact_ids',
        'source_id',
        'stage',
    ]

    def format_data_get(self):
        pass


class DealSet(CollectionV1):
    API_VERSION = 1
    _PATH = "deal"
    FILTERS = {
        'currency',
        'stage',
        'tag_ids',
        # tags (e.g. tag text) not available in deals
        'user_id',
        'hot',
    }
    ORDERS = [
        'account_id',
        'added_on',
        'created_at',
        'currency',
        'entity_id',
        'hot',
        'id',
        'last_activity',  # Alias for (otherwise not available) updated_at
        'last_stage_change_at',
        'loss_reason_id',
        'name',
        'scope',
        'source_id',
        'stage_code',
        'user_id'
        # In sort_value if submitted, otherwise not returned:
        'source',
        # Pulls full source record (user_id, name, created_at, updated_at, created_via, deleted_at, id, account_id
    ]

    def format_data_set(self):
        data = deepcopy(self.filters)
        if 'city' in data:
            data['city'] = str(data['city']).lower()
        if 'region' in data:
            data['region'] = str(data['region']).lower()
        if 'country' in data:
            data['country'] = str(data['country']).lower()


