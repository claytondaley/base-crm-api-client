#!/usr/bin/env python
"""Legacy procedural codebase, retained during functional migration"""

import logging
logger = logging.getLogger(__name__)

from prototypes import _key_coded_dict

__author__ = 'Nathan Pinger, Clayton C. Daley III'
__copyright__ = "Copyright 2012-2015 Nathan Pinger, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "1.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


class LegacyService(object):
    ##########################
    # Resource Builders
    #
    # BaseCRM has started to transition object identification from the path to the parameters (or a combination).  In
    # response, URL builder functions (returning just a url string) are being replaced with "resource" functions
    # returning a tuple of URL string (excluding parameters) and parameter dict.
    ##########################
    def _build_resource_url(self, resource, version, path=''):
        """
        Builds a URL for a resource using the not-officially-documented format:
            https://app.futuresimple.com/apis/<resource>/api/v<version>/<path>.<format>
        """
        if version == 2:
            if self.debug:
                url = 'https://api.sandbox.getbase.com/v%d%s' % (version, path)
            else:
                url = 'https://api.getbase.com/v%d%s' % (version, path)
        else:
            url = 'https://app.futuresimple.com/apis/%s/api/v%d%s' % (resource, version, path)
        return self._apply_format(url, self.format)

    def _build_search_url(self, type):
        if type == 'contact':
            url, params = self._build_contact_resource()
        elif type == 'deal':
            url, params = self._build_deal_resource()
        elif type == 'lead':
            url, params = self._build_lead_resource()
        else:
            raise ValueError("Invalid search type.")
        url += '/search'
        return self._apply_format(url, self.format)

    ##########################
    # Feed (i.e. Activity) Functions
    #
    # NOTE: feeds overlap to some degree with tasks (completed only) and notes
    ##########################
    def _build_feed_resource(self, contact_id=None, lead_id=None, deal_id=None, type=None, timestamp=None):
        """
        Returns a tuple of URL (without parameters) and params that will produce a list of activities (i.e. feed) in
        batches of 20.

        ARGUMENTS

        Parent objects (optional, include only one):
            contact_id (default None) - load activities for a specific contact
            lead_id (default None) - load activities for a specific lead
            deal_id (default None) - load activities for a specific deal
        Activity Types:
            type=None (default) - load all types
            type='Email' - returns only emails
            type='Note' - returns only notes
            type='Call' - returns only phone calls
            type='Task' - returns only completed tasks
        Paging:
            timestamp - feed paging is achieved using the timestamp parameter, not a traditional page number (see the
                stateful client for automatic handling of feed paging

        RESPONSE STRUCTURE

        see get_feed()
        """
        path = '/feed'
        url_params = dict()

        url_params['api_mailman'] = 'v2'

        if timestamp is not None:
            url_params['timestamp'] = timestamp

        if contact_id is not None:
            path += "/contact/%d" % contact_id
        elif lead_id is not None:
            path += "/lead/%d" % lead_id
        elif deal_id is not None:
            path += "/deal/%d" % deal_id

        if type is not None:
            if type in ['Email', 'Note', 'Call', 'Task']:
                url_params['only'] = type
            else:
                raise ValueError(
                    "'%s' is not a valid type, must be None, 'Email', 'Note', 'Call', or 'Task'" % str(type))

        url_noparam = self._build_resource_url('feeder', 1, path, self.format)
        return url_noparam, url_params

    def _get_feed(self, contact_id=None, lead_id=None, deal_id=None, type=None, timestamp=None):
        """
        Returns the most recent 20 activities (i.e. feed) that meet the filter conditions

        ARGUMENTS

        Parent Objects (optional, include only one):
            contact_id (default None) - load activities for a specific contact
            lead_id (default None) - load activities for a specific lead
            deal_id (default None) - load activities for a specific deal
        Activity Types:
            type=None (default) - load all types
            type='Email' returns only emails
            type='Note' returns only notes
            type='Call' returns only phone calls
            type='Task' returns only completed tasks
        Paging:
            timestamp - feed paging is achieved using the timestamp parameter, not a traditional page number (see the
                stateful client for automatic handling of feed paging
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        RESPONSE STRUCTURE

        see get_feed()
        """
        url_noparam, url_params = self._build_feed_resource(contact_id=contact_id, deal_id=deal_id, lead_id=lead_id,
                                                            type=type, timestamp=timestamp)
        return self._get_data(url_noparam, url_params)

    def get_feed(self, type=None, timestamp=None):
        """
        Returns the most recent 20 activities (i.e. feed) that meet the filter conditions

        ARGUMENTS

        Activity Types:
            type=None (default) - load all types
            type='Email' returns only emails
            type='Note' returns only notes
            type='Call' returns only phone calls
            type='Task' returns only completed tasks
        Paging:
            timestamp - feed paging is achieved using the timestamp parameter, not a traditional page number (see the
                stateful client for automatic handling of feed paging

        RESPONSE STRUCTURE

        {'items':
            [{'feed_item':
                {'attributes': {...} # Depends on object type, see attributes below
                 'api': ... # 'v1' or 'v2'
                 'type': ... # 'lead', 'note', 'deal', 'contact', 'deal_stage_change', 'synced_email'...
                 'sorted_by': ... # the value of the field on which the item was sorted
                }
              'success': ...
              'metadata': ...
            }, ...]
         'success': ...
         'metadata': ...
        }

        ATTRIBUTES DICTIONARY KEYS

        For 'lead':
        'first_name', 'last_name', 'user_id', 'account_id', 'state', 'created_at', 'status_id', 'updated_at',
        'has_any_email', 'last_activity_date', 'created_via', 'company_name', 'deleted_at', 'id', 'owner_id'

        For 'deal':
        'user_id', 'account_id', 'created_at', 'currency', 'creator_id', 'scope', 'id', 'name'

        For 'contact':
        'first_name', 'last_name', 'user_id', 'name', 'title', 'mobile', 'created_at', 'is_sales_account', 'contact_id',
        'email', 'phone', 'creator_id', 'id', 'account_id'

        For 'note':
        'user_id', 'account_id', 'permissions_holder_id', 'created_at', 'updated_at', 'noteable_type', 'content',
        'private', 'noteable_id', 'id'

        For 'deal_stage_change':
        'user_id', 'account_id', 'created_at', 'to_stage_name', 'to_stage', 'from_stage', 'from_stage_name', 'id',
        'deal_id'

        For 'synced_email':
        ['status', 'addresses', 'from', 'sender', 'to', 'synced_email_thread_id', 'created_at', 'attachments', 'bcc',
        'content', 'sha', 'mailbox_type', 'reply_to', 'related_objects', 'date', 'seen', 'internal_forwarded_from',
        'id', 'cc', 'subject']

        """
        return self._get_feed(type=type, timestamp=timestamp)

    def get_contact_feed(self, contact_id, timestamp=None):
        return self._get_feed(contact_id=contact_id, timestamp=timestamp)

    def get_contact_feed_emails(self, contact_id, timestamp=None):
        return self._get_feed(contact_id=contact_id, type='Email', timestamp=timestamp)

    def get_contact_feed_notes(self, contact_id, timestamp=None):
        return self._get_feed(contact_id=contact_id, type='Note', timestamp=timestamp)

    def get_contact_feed_calls(self, contact_id, timestamp=None):
        return self._get_feed(contact_id=contact_id, type='Call', timestamp=timestamp)

    def get_contact_feed_tasks_completed(self, contact_id, timestamp=None):
        return self._get_feed(contact_id=contact_id, type='Task', timestamp=timestamp)

    def get_deal_feed(self, deal_id, timestamp=None):
        return self._get_feed(deal_id=deal_id, timestamp=timestamp)

    def get_deal_feed_emails(self, deal_id, timestamp=None):
        return self._get_feed(deal_id=deal_id, type='Email', timestamp=timestamp)

    def get_deal_feed_notes(self, deal_id, timestamp=None):
        return self._get_feed(deal_id=deal_id, type='Note', timestamp=timestamp)

    def get_deal_feed_calls(self, deal_id, timestamp=None):
        return self._get_feed(deal_id=deal_id, type='Call', timestamp=timestamp)

    def get_deal_feed_tasks_completed(self, deal_id, timestamp=None):
        return self._get_feed(deal_id=deal_id, type='Task', timestamp=timestamp)

    def get_lead_feed(self, lead_id, timestamp=None):
        return self._get_feed(lead_id=lead_id, timestamp=timestamp)

    def get_lead_feed_emails(self, lead_id, timestamp=None):
        return self._get_feed(lead_id=lead_id, type='Email', timestamp=timestamp)

    def get_lead_feed_notes(self, lead_id, timestamp=None):
        return self._get_feed(lead_id=lead_id, type='Note', timestamp=timestamp)

    def get_lead_feed_notes_alt(self, lead_id, timestamp=None):
        return self._get_notes(lead_id=lead_id, timestamp=timestamp)

    def get_lead_feed_calls(self, lead_id, timestamp=None):
        return self._get_feed(lead_id=lead_id, type='Call', timestamp=timestamp)

    def get_lead_feed_tasks_completed(self, lead_id, timestamp=None):
        return self._get_feed(lead_id=lead_id, type='Task', timestamp=timestamp)

    ##########################
    # Tags Functions
    ##########################
    def _build_tags_resource(self, tag_id=None, app_id=None, page=None):
        """
        Returns a tuple of URL (without parameters) and params to obtain a list of tags in batches of 20

        ARGUMENTS

        Filters:
            tag_id - returns information about a single tag
            app_id - gets all tags for a particular app_id (i.e. type of object)
        Paging:
            page (default 1)
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        RESPONSE STRUCTURE

        see get_tags()
        """
        path = '/tags'
        url_params = dict()

        if tag_id is not None:
            path += '/%s' % tag_id
        elif app_id is not None:
            url_params['app_id'] = app_id

        if page is not None:
            url_params['page'] = page

        url_noparam = self._build_resource_url('tags', 1, path)
        return url_noparam, url_params

    def get_tags(self, type, page=1):
        """
        Gets tag objects for a particular type of object in batches of 20

        ARGUMENTS

        Type:
            type='Contact'
            type='ContactAlt' - Due to a quirk in the backend, contact tags appear to have two access methods which
                have been duplicated in the API client in case they are functional
            type='Deal'
            type='Lead'
        Paging
            page (default 1)

        RESPONSE STRUCTURE

        [{'tag':
            {'id': ...
             'name': ...
             'permissions_holder_id': ...
            }
        }, ...]
        """
        # Translates between object types and friendly names
        if type == 'Contact':
            # https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=4
            app_id = 4
        elif type == 'ContactAlt':
            # https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=7
            app_id = 7
        elif type == 'Deal':
            # https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=1
            app_id = 1
        elif type == 'Lead':
            # https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=5
            app_id = 5
        else:
            raise ValueError("type was '%s' but must be 'Contact', 'ContactAlt', 'Deal', or 'Lead'" % str(type))

        url_noparam, url_params = self._build_tags_resource(app_id=app_id, page=page)
        return self._get_data(url_noparam, url_params)

    def get_tag(self, tag_id):
        """
        Returns the contents of one tag identified by tag_id

        RESPONSE STRUCTURE

        {'tag':
            {'id': ...
             'name': ...
             'permissions_holder_id': ...
            }
        }
        """
        url_noparam, url_params = self._build_tags_resource(tag_id=tag_id)
        return self._get_data(url_noparam, url_params)

    def get_contact_tags(self, page=1):
        """
        Returns tags associated with Contacts in batches of 20

        NOTE: Due to an underlying ambiguity in the API, see also get_contact_tags_alt()
        """
        return self.get_tags('Contact', page)

    def get_contact_tags_alt(self, page=1):
        """
        Returns tags associated with Contacts in batches of 20

        NOTE: Due to an underlying ambiguity in the API, see also get_contact_tags()
        """
        return self.get_tags('ContactAlt', page)

    def get_deal_tags(self, page=1):
        """
        Returns tags associated with Deals in batches of 20
        """
        return self.get_tags('Deal', page)

    def get_lead_tags(self, page=1):
        """
        Returns tags associated with Leads in batches of 20
        """
        return self.get_tags('Lead', page)

    def _upsert_tag(self):
        raise NotImplementedError

    def update_tag(self):
        raise NotImplementedError

    def create_contact_tag(self):
        app_id = 4
        raise NotImplementedError

    def create_deal_tag(self):
        app_id = 1
        raise NotImplementedError

    def create_lead_tag(self):
        app_id = 5
        raise NotImplementedError

    def _build_taggings_resource(self, tag_list, method='add', contact_id=None, deal_id=None, lead_id=None,
                                 contact_ids=None, deal_ids=None, lead_ids=None):
        """
        Returns a tuple of URL (without parameters) and params to modify object tags

        ARGUMENTS

        Behavior:
            tag_list - list of one to many tags (
            method (default 'add') - determines the change made ('add', 'remove', or 'replace')
        Parent Objects (only valid for 'replace', include only one)
            contact_id
            deal_id
            lead_id
        Parent Objects (only valid for 'add' and 'remove', include only one)
            contact_ids
            deal_ids
            lead_ids
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        RESPONSE STRUCTURE

        see _add_tags(), _remove_tag(), _replace_tags()
        """
        path = '/taggings'
        url_params = dict()

        url_params['tag_list'] = ','.join(tag_list)

        # Configure parameters for method and target object (together because there are strict compatibilities)
        if method == 'replace':
            # Only singular id values are compatible
            if contact_id is not None:
                url_params['taggable_id'] = contact_id
                url_params['taggable_type'] = 'Contact'
            elif deal_id is not None:
                url_params['taggable_id'] = deal_id
                url_params['taggable_type'] = 'Deal'
            elif lead_id is not None:
                url_params['taggable_id'] = lead_id
                url_params['taggable_type'] = 'Lead'
        elif method in ['add', 'remove']:
            if method == 'add':
                path += '/batch_add'
            else:  # method == 'replace'
                path += '/batch_untag'
            # Only plural ids values are compatible
            if contact_ids is not None:
                url_params['taggable_ids'] = ','.join([str(x) for x in contact_ids])
                url_params['taggable_type'] = 'Contact'
            elif deal_ids is not None:
                url_params['taggable_ids'] = ','.join([str(x) for x in deal_ids])
                url_params['taggable_type'] = 'Deal'
            elif lead_ids is not None:
                url_params['taggable_ids'] = ','.join([str(x) for x in lead_ids])
                url_params['taggable_type'] = 'Lead'
        else:
            raise ValueError("'method' is '%s' but must be 'add', 'remove', or 'replace'" % str(method))

        if url_params['taggable_type'] == 'Contact':
            url_params['app_id'] = 4
        elif url_params['taggable_type'] == 'Deal':
            url_params['app_id'] = 1
        elif url_params['taggable_type'] == 'Lead':
            url_params['app_id'] = 5

        url_noparam = self._build_resource_url('tags', 1, path)
        return url_noparam, url_params

    def _add_tags(self, tag_list, contact_id=None, deal_id=None, lead_id=None,
                  contact_ids=None, deal_ids=None, lead_ids=None):
        """
        PRIVATE FUNCTION that enforces data integrity rules for adding tags, to be called by public single-purpose tag
        functions.

        ARGUMENTS

        Tags:
            tag_list - list of textual tags
        Parent Object(s) (include only one):
            contact_id - singular id
            deal_id - singular id
            lead_id - singular id
            contact_ids - list of ids
            deal_ids - list of ids
            lead_ids - list of ids

        RESPONSE STRUCTURE

        {'<taggable_id_1>':
            ['<new tag 1>',
             '<new tag 2>'
            ],
         ...
        }

        NOTE: In the response dict, a key is present for each submitted object.  The value is a list of tags actually
        added to the object.  If no tags were added to a particular object, the value is an empty list.
        """
        method = 'add'
        if not isinstance(tag_list, list):
            tag_list = [tag_list]
        else:
            # Ensure None (if present) is not translated into a string
            # lower() because UI implementation of tags seems to assume case insensitivity, but API is case sensitive
            tag_list = [str(x).lower() for x in tag_list if x]

        contacts, deals, leads = None, None, None
        # Support both singleton id and list ids
        if contact_id is not None:
            contacts = [contact_id]
        elif deal_id is not None:
            deals = [deal_id]
        elif lead_id is not None:
            leads = [lead_id]
        elif contact_ids is not None:
            contacts = contact_ids
        elif deal_ids is not None:
            deals = deal_ids
        elif lead_ids is not None:
            leads = lead_ids
        else:
            raise ValueError('_add_tags request must include a valid object')

        url_noparam, url_params = self._build_taggings_resource(tag_list=tag_list, method=method,
                                                                contact_ids=contacts, deal_ids=deals, lead_ids=leads)
        return self._post_data(url_noparam, url_params)

    def _remove_tag(self, tag, contact_id=None, deal_id=None, lead_id=None,
                    contact_ids=None, deal_ids=None, lead_ids=None):
        """
        PRIVATE FUNCTION that enforces data integrity rules for removing tags, to be called by public single-purpose
        tag functions.

        ARGUMENTS

        Tags:
            tag - single textual tag
        Parent Object(s) (include only one):
            contact_id - singular id
            deal_id - singular id
            lead_id - singular id
            contact_ids
            deal_ids
            lead_ids

        RESPONSE STRUCTURE

        {'untagged_ids': null}

        OR

        {'untagged_ids':
            [<object_id 1>,
            ...
            ]
        }

        NOTE: Only includes objects where the tag was removed.  If no objects were affected, the value of
        'untagged_ids' is None (rather than an empty list).
        """
        method = 'remove'
        # The remove method only supports a single tag.  Since most other tag methods support lists of tags, we
        # explicitly check that the input in valid.
        if isinstance(tag, list):
            raise ValueError("'tag' does not accept a list")
        if ',' in tag:
            raise ValueError("'tag' may not include a comma as only one tag can be removed at a time")

        # _build_taggings_resource only accepts a list of tags so we recast our single tag appropriately
        if tag:  # ensure None is not translated into a string
            # lower() because UI implementation of tags seems to assume case insensitivity, but API is case sensitive
            tag = [str(tag).lower()]
        else:
            tag = []  # The API considers this a valid request so we don't bother raising an error

        url_noparam, url_params = self._build_taggings_resource(tag_list=tag, method=method, contact_id=contact_id,
                                                                deal_id=deal_id, lead_id=lead_id,
                                                                contact_ids=contact_ids, deal_ids=deal_ids,
                                                                lead_ids=lead_ids)
        return self._post_data(url_noparam, url_params)

    def _replace_tags(self, tag_list, contact_id=None, deal_id=None, lead_id=None):
        """
        PRIVATE FUNCTION that enforces data integrity rules for replacing tags, to be called by public single-purpose
        tag functions.

        ARGUMENTS

        Tags:
            tag_list - list of textual tags
        Parent Object (include only one):
            contact_id
            deal_id
            lead_id

        RESPONSE STRUCTURE

        [{'tag':
            {'id': ...
             'name': ...
             'permissions_holder_id': ...
             }
         }, ...]

        NOTE: Lists ids of all tags included in tag_list
        """
        method = 'replace'
        if not isinstance(tag_list, list):
            raise ValueError("'tag_list' must be a list")
        else:
            # Ensure None (if present) is not translated into a string
            # lower() because UI implementation of tags seems to assume case insensitivity, but API is case sensitive
            tag_list = [str(x).lower() for x in tag_list if x]

        url_noparam, url_params = self._build_taggings_resource(tag_list=tag_list, method=method, contact_id=contact_id,
                                                                deal_id=deal_id, lead_id=lead_id)
        return self._post_data(url_noparam, url_params)

    def tag_contacts(self, tag_list, contact_ids):
        """
        Adds one or more tags to one or more contacts

        ARGUMENTS

            tag_list - list of tags (text form, not ids)
            contact_ids - list of IDs or single ID (automatically converted to a one-item list)

        RESPONSE STRUCTURE

        see _add_tags()
        """
        if not isinstance(contact_ids, list):
            contact_ids = [contact_ids]
        return self._add_tags(tag_list=tag_list, contact_ids=contact_ids)

    def untag_contacts(self, tag, contact_ids):
        """
        Removes one tag from one or more contacts

        ARGUMENTS

            tag - single tag (text form, not ids)
            contact_ids - list of IDs or single ID (automatically converted to a one-item list)

        RESPONSE STRUCTURE

        see _remove_tag()
        """
        if not isinstance(contact_ids, list):
            contact_ids = [contact_ids]
        return self._remove_tag(tag=tag, contact_ids=contact_ids)

    def retag_contact(self, tag_list, contact_id):
        """
        Replaces all tags for contact_id with tags in tag_list

        ARGUMENTS

            tag_list - list of tags (text form, not ids)
            contact_id - id of contact to be updated

        RESPONSE STRUCTURE

        see _replace_tags()
        """
        return self._replace_tags(tag_list=tag_list, contact_id=contact_id)

    def update_contact_tags(self, tag_list, contact_id):
        """
        Alias for retag_contact():  Replaces all tags for contact_id with tags in tag_list
        """
        return self.retag_contact(tag_list=tag_list, contact_id=contact_id)

    def tag_deals(self, tag_list, deal_ids):
        """
        Adds one or more tags to one or more deals

        ARGUMENTS

            tag_list - list of tags (text form, not ids)
            deal_ids - list of IDs or single ID (automatically converted to a one-item list)

        RESPONSE STRUCTURE

        see _add_tags()
        """
        if not isinstance(deal_ids, list):
            deal_ids = [deal_ids]
        return self._add_tags(tag_list=tag_list, deal_ids=deal_ids)

    def untag_deals(self, tag, deal_ids):
        """
        Removes one tag from one or more deals

        ARGUMENTS

            tag - single tag (text form, not ids)
            deal_ids - list of IDs or single ID (automatically converted to a one-item list)

        RESPONSE STRUCTURE

        see _remove_tag()
        """
        if not isinstance(deal_ids, list):
            deal_ids = [deal_ids]
        return self._remove_tag(tag=tag, deal_ids=deal_ids)

    def retag_deal(self, tag_list, deal_id):
        """
        Replaces all tags for deal_id with tags in tag_list

        ARGUMENTS

            tag_list - list of tags (text form, not ids)
            deal_id - id of deal to be updated

        RESPONSE STRUCTURE

        see _replace_tags()
        """
        return self._replace_tags(tag_list=tag_list, deal_id=deal_id)

    def update_deal_tags(self, tag_list, deal_id):
        """
        Alias for retag_deal():  Replaces all tags for deal_id with tags in tag_list
        """
        return self.retag_deal(tag_list=tag_list, deal_id=deal_id)

    def tag_leads(self, tag_list, lead_ids):
        """
        Adds one or more tags to one or more leads

        ARGUMENTS

            tag_list - list of tags (text form, not ids)
            lead_ids - list of IDs or single ID (automatically converted to a one-item list)

        RESPONSE STRUCTURE

        see _add_tags()
        """
        if not isinstance(lead_ids, list):
            lead_ids = [lead_ids]
        return self._add_tags(tag_list=tag_list, lead_ids=lead_ids)

    def untag_leads(self, tag, lead_ids):
        """
        Removes one tag from one or more leads

        ARGUMENTS

            tag - single tag (text form, not ids)
            lead_ids - list of IDs or single ID (automatically converted to a one-item list)

        RESPONSE STRUCTURE

        see _remove_tag()
        """
        if not isinstance(lead_ids, list):
            lead_ids = [lead_ids]
        return self._remove_tag(tag=tag, lead_ids=lead_ids)

    def retag_lead(self, tag_list, lead_id):
        """
        Replaces all tags for lead_id with tags in tag_list

        ARGUMENTS

            tag_list - list of tags (text form, not ids)
            lead_id - id of lead to be updated

        RESPONSE STRUCTURE

        see _replace_tags()
        """
        return self._replace_tags(tag_list=tag_list, lead_id=lead_id)

    def update_lead_tags(self, tag_list, lead_id):
        """
        Alias for retag_lead():  Replaces all tags for lead_id with tags in tag_list
        """
        return self.retag_lead(tag_list=tag_list, lead_id=lead_id)

    ##########################
    # Notes Functions
    #
    # NOTE: notes overlap to some degree with feeds
    ##########################
    def _build_note_resource(self, note_id=None, contact_id=None, deal_id=None, lead_id=None, page=None):
        """
        Returns a tuple of URL (without parameters) and params to get notes matching filter criteria in batches of 20

        Parent Objects (optional, include only one):
            contact_id
            deal_id
            lead_id
        Paging:
            page (default 1): the page of results to be loaded
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        Returns a URL to obtain either all notes (note_id=None) or a specific note (note_id=integer). This call must
        include a format:
         - SEE BaseAPIService._apply_format() FOR ACCEPTED VALUES
        """
        path = '/notes'
        url_params = dict()

        if note_id is not None:
            path += '/%s' % note_id
        elif contact_id is not None:
            url_params['noteable_type'] = 'Contact'
            url_params['noteable_id'] = contact_id
        elif deal_id is not None:
            url_params['noteable_type'] = 'Deal'
            url_params['noteable_id'] = deal_id
        elif lead_id is not None:
            url_params['noteable_type'] = 'Lead'
            url_params['noteable_id'] = lead_id

        if page is not None:
            url_params['page'] = page

        url_noparam = self._build_resource_url('common', 1, path, format)
        return url_noparam, url_params

    def _get_notes(self, note_id=None, contact_id=None, deal_id=None, lead_id=None, page=None):
        """
        PRIVATE FUNCTION to get notes that can be called by public, single-purpose notes functions.

        RESPONSE STRUCTURE

        see get_notes(), get_note()
        """
        url_noparam, url_params = self._build_note_resource(note_id=note_id, contact_id=contact_id, deal_id=deal_id,
                                                            lead_id=lead_id, page=page)
        return self._get_data(url_noparam, url_params)

    def get_notes(self, page=1):
        """
        Returns notes visible to the authenticated user in batches of 20.  To filter by object type or ID see
        get_contact_notes(), get_lead_notes(), and get_deal_notes().

        ARGUMENTS

        Paging:
            page

        RESPONSE STRUCTURE

        [{'note':
            {'user_id': ...
             'account_id': ...
             'permissions_holder_id': ...
             'created_at': ...
             'updated_at': ...
             'noteable_id': ...
             'noteable_type': ...
             'content': ...
             'private': ...
             'id': ...
            }
        }, ...]
        """
        return self._get_notes(page=page)

    def get_note(self, note_id):
        """
        Gets the attributes for the given note_id

        RESPONSE STRUCTURE

        {'note':
            {'user_id': ...
             'account_id': ...
             'permissions_holder_id': ...
             'created_at': ...
             'updated_at': ...
             'noteable_id': ...
             'noteable_type': ...
             'content': ...
             'private': ...
             'id': ...
            }
        }
        """
        return self._get_notes(note_id=note_id)

    def _upsert_note(self, content, note_id=None, contact_id=None, deal_id=None, lead_id=None):
        """
        PRIVATE FUNCTION to create or update notes

        ATTRIBUTES

        Content:
            content - body of note
        Note Object or Parent Object (must include one, include only one):
            note_id
            contact_id
            deal_id
            lead_id
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        RESPONSE STRUCTURE

        see get_note()

        NOTE that all objects must be encoded as note[<field>] without the quotes normally introduced by URL encoding
        python dicts.
        """
        url_noparams, note_params = self._build_note_resource(note_id=note_id, contact_id=contact_id, deal_id=deal_id,
                                                              lead_id=lead_id)

        note_params['content'] = content
        url_params = _key_coded_dict({'note': note_params})

        if note_id is None:
            return self._post_data(url_noparams, url_params)
        else:
            return self._put_data(url_noparams, url_params)

    def update_note(self, content, note_id):
        """
        Updates the content for the given note_id

        ATTRIBUTES

            note_id - id of note being modified
            content - the new content for the note

        RESPONSE STRUCTURE

        see get_note()
        """
        self._upsert_note(content=content, note_id=note_id)

    def get_contact_notes(self, contact_id, page=0):
        """
        Gets all notes associated with a specific contact (defined by Base's unique contat_id) in batches of 20

        RESPONSE STRUCTURE

        see get_note()
        """
        return self._get_notes(contact_id=contact_id, page=page)

    def create_contact_note(self, content, contact_id):
        """
        Creates a note associated with a specific contact (defined by Base's unique contact_id)
        with the content 'content'.

        RESPONSE STRUCTURE

        see get_note()
        """
        return self._upsert_note(content=content, contact_id=contact_id)

    def update_contact_note(self, content, note_id):
        """
        Edits a note (the note's unique note_id) with the content content.
        Returns a json or xml response.

        RESPONSE STRUCTURE

        see get_note()
        """
        return self._upsert_note(content=content, note_id=note_id)

    def get_deal_notes(self, deal_id, page=0):
        return self._get_notes(deal_id=deal_id, page=page)

    def create_deal_note(self, content, deal_id):
        """
        Creates a note associated with a specific deal (defined by Base's unique deal_id)
        with the content 'content'.
        Returns a json or xml response.
        """
        return self._upsert_note(content=content, deal_id=deal_id)

    def update_deal_note(self, content, note_id):
        """
        Edits a note (defined by Base's unique deal_id and the note's unique note_id)
        with the content content.
        Returns a json or xml response.
        """
        return self._upsert_note(content=content, note_id=note_id)

    def get_lead_notes(self, lead_id, page=0):
        return self._get_notes(lead_id=lead_id, page=page)

    def create_lead_note(self, content, lead_id):
        """
        Creates a note associated with a specific lead (defined by Base's unique lead_id)
        with the content 'content'.
        Returns a json or xml response.
        """
        return self._upsert_note(content=content, lead_id=lead_id)

    def update_lead_note(self, content, note_id):
        """
        Edits a note (the note's unique note_id) with the content content.
        Returns a json or xml response.

        RESPONSE STRUCTURE

        see get_note()
        """
        return self._upsert_note(content=content, note_id=note_id)

    ##########################
    # Tasks Functions
    #
    # NOTE: tasks overlap to some degree with feeds (completed only)
    ##########################

    TASK_STATUS_OPTIONS = ['active', 'done']
    TASK_DUE_OPTIONS = ['today', 'tomorrow', 'this_week', 'overdue', 'no_due_date']

    # Count
    # https://app.futuresimple.com/apis/common/api/v1/tasks/context_count.json?page=1&status=done&_=1394056005668

    def _build_task_resource(self, task_id=None, contact_id=None, lead_id=None, deal_id=None, status=None, due=None,
                             due_range=None, page=1):
        """
        Returns a tuple of URL (without parameters) and params to get tasks in batches of 20.

        ARGUMENTS

        ...
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        RESPONSE STRUCTURE

        see get_tasks()
        """
        path = '/tasks'
        url_params = dict()

        if task_id is not None:
            path += '/%s' % task_id
        elif contact_id is not None:
            url_params['taskable_type'] = 'Contact'
            url_params['taskable_id'] = contact_id
        elif deal_id is not None:
            url_params['taskable_type'] = 'Deal'
            url_params['taskable_id'] = deal_id
        elif lead_id is not None:
            url_params['taskable_type'] = 'Lead'
            url_params['taskable_id'] = lead_id

        if due is not None:
            if due in self.TASK_DUE_OPTIONS:
                url_params['date'] = due
            else:
                raise ValueError("'due' is set to '%s', but only accepts: '%s'" % str(due),
                                 "', '".join(self.TASK_DUE_OPTIONS))
        elif due_range is not None:
            if isinstance(due_range, tuple):
                if len(due_range) == 2:
                    if due_range[0] > due_range[1]:
                        url_params['send_time_from'] = due_range[1]
                        url_params['send_time_to'] = due_range[0]
                    else:
                        url_params['send_time_from'] = due_range[0]
                        url_params['send_time_to'] = due_range[1]
                else:
                    raise ValueError("'due_range' must have length 2")
            else:
                raise ValueError("'due_range' must be a tuple")

        if status is not None:
            if status in self.TASK_STATUS_OPTIONS:
                url_params['status'] = status
            else:
                raise ValueError("'status' is set to '%s', but only accepts: '%s'" % str(status),
                                 "', '".join(self.TASK_STATUS_OPTIONS))

        if page == -1:
            url_params['skip_pagination'] = True
        else:
            url_params['page'] = page

        url_params['page'] = page

        url_noparam = self._build_resource_url('common', 1, path)
        return url_noparam, url_params

    def _get_tasks(self, task_id=None, contact_id=None, lead_id=None, deal_id=None, status=None, due=None,
                   due_range=None, page=1):
        """
        PRIVATE FUNCTION to get tasks that can be called by public, single-purpose tasks functions.

        RESPONSE STRUCTURE

        see get_tasks(), get_task()
        """
        url_noparam, url_params = self._build_task_resource(task_id=task_id, contact_id=contact_id, lead_id=lead_id,
                                                            deal_id=deal_id, status=status, due=due,
                                                            due_range=due_range, page=page)
        return self._get_data(url_noparam, url_params)

    def get_tasks(self, status=None, due=None, page=1):
        """
        Returns tasks visible to the authenticated user in batches of 20.  To filter by object type or ID see
        get_contact_tasks(), get_lead_tasks(), and get_deal_tasks().

        ARGUMENTS

        RESPONSE STRUCTURE

        [{task:
            {'due_date': ...
             'is_overdue': ...
             'user_id': ...
             'account_id': ...
             'hour': ...
             'taskable_type': ...
             'created_at': ...
             'send_time': ...
             'updated_at': ...
             'content': ...
             'remind': ...
             'taskable_id': ...
             'permissions_holder_id': ...
             'done_at': ...
             'date': ...
             'done': ...
             'id': ...
             'owner_id': ...
            }
        }, ...]

        """
        return self._get_tasks(status=status, due=due, page=page)

    def get_tasks_by_date_range(self, due_from, due_to, status=None, page=1):
        """
        Gets all tasks meeting criteria in groups of 20

        ARGUMENTS

        Date Range (automatically detects order)
            date_from - tested with values of type datetime.datetime()
            date_to - tested with values of type datetime.datetime()
        Status
            status=None - all tasks
            status='active' - incomplete tasks
            status='done' - completed tasks
        Other
            page (default 1)

        RESPONSE STRUCTURE

        see get_tasks()
        """
        return self._get_tasks(status=status, due_range=(due_from, due_to), page=page)

    def get_task(self, task_id):
        """
        Returns the attributes of task identified by task_id

        RESPONSE STRUCTURE

        {task:
            {'due_date': ...
             'is_overdue': ...
             'user_id': ...
             'account_id': ...
             'hour': ...
             'taskable_type': ...
             'created_at': ...
             'send_time': ...
             'updated_at': ...
             'content': ...
             'remind': ...
             'taskable_id': ...
             'permissions_holder_id': ...
             'done_at': ...
             'date': ...
             'done': ...
             'id': ...
             'owner_id': ...
            }
        }
        """
        return self._get_tasks(task_id=task_id)

    # Relocate
    def get_contact_tasks(self, contact_id):
        return self._get_tasks(contact_id=contact_id)

    def get_deal_tasks(self, deal_id):
        return self._get_tasks(deal_id=deal_id)

    def get_lead_tasks(self, lead_id):
        return self._get_tasks(lead_id=lead_id)

    def _upsert_task(self, task_info, task_id=None, contact_id=None, lead_id=None, deal_id=None):
        """
        PRIVATE FUNCTION to create or update a task

        ARGUMENTS

            task_info - dict of fields
            task_id (optional) - task being updated (otherwise it will be created)
        Parent object (choose one and only one):
            contact_id
            lead_id
            deal_id
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        RESPONSE STRUCTURE

        see get_task()
        """
        url_noparam, url_params = self._build_task_resource(task_id=task_id, contact_id=contact_id,
                                                            lead_id=lead_id, deal_id=deal_id)
        if contact_id is not None:
            task_info['taskable_type'] = 'Contact'
            task_info['taskable_id'] = contact_id
        elif deal_id is not None:
            task_info['taskable_type'] = 'Deal'
            task_info['taskable_id'] = deal_id
        elif lead_id is not None:
            task_info['taskable_type'] = 'Lead'
            task_info['taskable_id'] = lead_id
        url_params = _key_coded_dict({'task': task_info})
        if task_id is None:
            return self._post_data(url_noparam, url_params)
        else:
            return self._put_data(url_noparam, url_params)

    def create_contact_task(self, task_info, contact_id):
        """
        Creates a new task based on task_info and assigns it to a contact
        """
        return self._upsert_task(task_info=task_info, contact_id=contact_id)

    def update_contact_task(self, task_info, task_id):
        """
        Updates task identified by task_id with information from task_info
        """
        return self._upsert_task(task_info=task_info, task_id=task_id)

    def create_deal_task(self, task_info, deal_id):
        """
        Creates a new task based on task_info and assigns it to a deal
        """
        return self._upsert_task(task_info=task_info, deal_id=deal_id)

    def update_deal_task(self, task_info, task_id):
        """
        Updates task identified by task_id with information from task_info
        """
        return self._upsert_task(task_info=task_info, task_id=task_id)

    def create_lead_task(self, task_info, lead_id):
        """
        Creates a new task based on task_info and assigns it to a lead
        """
        return self._upsert_task(task_info=task_info, lead_id=lead_id)

    def update_lead_task(self, task_info, task_id):
        """
        Updates task identified by task_id with information from task_info
        """
        return self._upsert_task(task_info=task_info, task_id=task_id)

    ##########################
    # Reminder Functions
    ##########################
    def _build_reminder_resource(self, reminder_id=None, contact_id=None, deal_id=None, format=None):
        """
        Returns a tuple of URL (without parameters) and params to get reminders meeting the filter criteria

        Parent Object (optional, include only one):
            contact_id
            lead_id
            deal_id
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values
        """
        path = ''
        url_params = dict()

        if contact_id is not None:
            path += '/contacts/%d' % contact_id
        elif deal_id is not None:
            path += '/deals/%d' % deal_id
        else:
            raise ValueError("Reminders URL constructor requires a valid object (lead, contact, deal).")
        path += '/reminders'
        if reminder_id is not None:
            path += '/%s' % reminder_id

        url_noparam = self._build_resource_url('sales', 1, path, format)
        return url_noparam, url_params

    def _get_reminder(self, reminder_id=None, contact_id=None, deal_id=None, format=None):
        url_noparam, url_params = self._build_reminder_resource(reminder_id=reminder_id, contact_id=contact_id,
                                                                deal_id=deal_id, format=format)
        return self._get_data(url_noparam, url_params)

    def get_contact_reminders(self, contact_id):
        return self._get_reminder(contact_id=contact_id)

    def get_deal_reminders(self, deal_id):
        return self._get_reminder(deal_id=deal_id)

    # API does not appear to support reminders for leads

    def _upsert_reminder(self, reminder_info, reminder_id=None, contact_id=None, deal_id=None, format=None):
        """
        PRIVATE FUNCTION to create or update a reminder

        ARGUMENTS

            reminder_info - dict of fields
            reminder_id (optional) - reminder being updated (otherwise it will be created)
        Parent object (choose one and only one):
            contact_id
            deal_id
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values
        """
        url_noparam, url_params = self._build_reminder_resource(reminder_id=reminder_id, contact_id=contact_id, deal_id=deal_id)
        url_params = _key_coded_dict({'reminder': reminder_info})
        if reminder_id is None:
            return self._post_data(url_noparam, url_params)
        else:
            return self._put_data(url_noparam, url_params)

    def create_contact_reminder(self, reminder_info, contact_id):
        """
        Creates a reminder based on reminder_info and assigns it to a contact
        """
        return self._upsert_reminder(reminder_info=reminder_info, contact_id=contact_id)

    def create_deal_reminder(self, reminder_info, deal_id):
        """
        Creates a reminder based on reminder_info and assigns it to a deal
        """
        return self._upsert_reminder(reminder_info=reminder_info, deal_id=deal_id)
    # Base returns error 500 when updating any kind of reminders

    ##########################
    # Contact Functions and Constants
    #
    # NOT YET IMPLEMENTED
    ##########################
    def _build_contact_resource(self, contact_id=None, contact_ids=None, company_id=None, deal_id=None,
                                page=1, per_page=None, format=None):
        """
        Returns a tuple of URL (without parameters) and params to get contacts that meet filter criteria in batches
        of 20

        ARGUMENTS

        Object or Parent Object (optional, include only one)
            deal_id - gets all contacts under the submitted deal_id
            contact_ids - list of contacts
            company_id - ID of the BaseCRM contact object for the parent company
        Paging:
            page (default 1)
            per_page (API default 20) - changes the batch size of pages
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values
        """
        path = '/contacts'
        url_params = dict()

        if deal_id is not None:
            # Nested under deals URL so we have to use an atypical construction
            url_noparam, ignore_params = self._build_deal_resource(deal_id)
            url_noparam += path
            self._apply_format(url_noparam, format)
        else:
            if contact_id is not None:
                # Creates contacts/<id> path required for updates
                path += '/%d' % contact_id
            elif contact_ids is not None:
                # Used by all get() callers to increase standardization of response
                url_params['contact_ids'] = ','.join(str(x) for x in contact_ids)
            elif company_id is not None:
                url_params['contact_id'] = company_id
            url_noparam = self._build_resource_url('crm', 1, path, format)

        url_params['page'] = page
        if per_page is not None:
            url_params['per_page'] = per_page

        return url_noparam, url_params

    def get_contacts(self, contact_ids=None, page=1, per_page=None):
        """
        Gets full contact records (38 fields) in batches of (default) 20.

        Arguments:
            page (default: 1) - the page of contacts to return
            per_page (default: 20) - the number of contacts to return per page
            contact_ids - allows the caller to specify a list of contacts to be returned

        Native response structure:
        [{'contact':
            {'account_id': ...
             'address': ...
             'city': ...
             'contact_id': ...
             'country': ...
             'created_at': ...
             'creator_id': ...
             'custom_fields': ...
             'description': ...
             'email': ...
             'facebook': ...
             'fax': ...
             'first_name': ...
             'id': ...
             'industry': ...
             'is_organisation': ...
             'is_sales_account': ...
             'last_name': ...
             'linkedin': ...
             'linkedin_display': ...
             'mobile': ...
             'name': ...
             'organisation': ...
             'organisation_name': ...
             'phone': ...
             'picture_url': ...
             'private': ...
             'region': ...
             'root_entity_id': ...
             'root_entity_name': ...
             'sales_account': ...
             'skype': ...
             'tags_joined_by_comma': ...
             'title': ...
             'twitter': ...
             'updated_at': ...
             'user_id': ...
             'website': ...
             'zip': ...
            }
        }, ...]
        """
        url_noparam, url_params = self._build_contact_resource(contact_ids=contact_ids, page=page, per_page=per_page)
        return self._get_data(url_noparam, url_params)

    def get_deal_contacts(self, deal_id, page=1, per_page=None):
        url_noparam, url_params = self._build_contact_resource(deal_id=deal_id, page=page, per_page=per_page)
        return self._get_data(url_noparam, url_params)

    def get_contact(self, contact_id):
        """
        Gets the contact with the given contact_id. Returns the contact info.
        """
        response = self.get_contacts(contact_ids=[contact_id])
        if len(response) > 0:
            return response[0]
        else:
            return None

    def search_contacts(self, filters=None, sort_by=None, sort_order='asc', tags_exclusivity='and', page=0):
        """
        Returns short (17 field) records for contacts meeting the filter criteria and ordered by sort criteria, in
        batches of 20

        ARGUMENTS

        Filter:
            filters - dict of filters (automatically joined by AND) where the key is the field name (see CONTACT_FILTERS
                for valid values) and the value is the matching criteria
            tags_exclusivity - if 'tags' or 'tag_ids' are included in the filter criteria, this determines whether the
                tags are combined using the AND or OR operator
        Sort:
            sort_by - a string identifying the field on which the responses should be sorted (see CONTACT_SORTS for
                valid values)
            sort_order - 'asc' or 'desc'
        Paging:
            page (default 0)

        RESPONSE STRUCTURE

        {'items':
            [{'contact':
                {'organisation_name': ...
                 'first_name': ...
                 'last_name': ...
                 'user_id': ...
                 'account_id': ...
                 'title': ...
                 'mobile': ...
                 'created_at': ...
                 'overdue_tasks': ...
                 'is_sales_account': ...
                 'id': ...
                 'phone': ...
                 'is_organisation': ...
                 'sort_value': ...
                 'email': ...
                 'unread_emails': ...
                 'name': ...
                }
            }, ...],
         'success': ...
         'metadata': ...
        }
        """
        url_noparam = self._build_search_url('contact')

        valid_params = {'page': page}
        if filters is not None:
            for key, value in filters.items():
                if key in self.CONTACT_FILTERS:
                    if key in ['tag_ids', 'tags']:
                        # tags are case sensitive
                        valid_params[key] = ','.join(value)
                        if tags_exclusivity in ['and', 'or']:
                            valid_params['tags_exclusivity'] = tags_exclusivity
                        else:
                            raise ValueError("tags_exclusivity must be 'and' or 'or'")
                    else:
                        # only lower case strings successfully match (regardless of original text case)
                        valid_params[key] = str(value).lower()
                else:
                    raise ValueError("%s is not a valid filter for a Contact search" % key)
        if sort_by is not None:
            if sort_by in self.CONTACT_SORTS:
                valid_params['sort_by'] = sort_by
            else:
                raise ValueError("%s is not a valid sort field for a Contact search" % sort_by)
            if sort_order in ['asc', 'desc']:
                valid_params['sort_order'] = sort_order
            else:
                raise ValueError("%s is not a valid sort order for a Contact search" % sort_order)

        return self._get_data(url_noparam, valid_params)

    def _upsert_contact(self, contact_info=None, contact_id=None):
        """
        Updates or Inserts a contact

        ARGUMENTS

            contact_info - dict of fields (see CONTACT_PARAMS for valid field names)
            contact_id (optional) - contact being updated (otherwise contact will be created)

        RESPONSE STRUCTURE

        see get_contact()
        """
        url_noparam, url_params = self._build_contact_resource(contact_id=contact_id)

        # If we are creating a new contact, we must have name and last_name parameters
        # and we always must have some parameter
        if contact_info is None or contact_info == {} or \
                (contact_id is None and 'name' not in contact_info.keys() and 'last_name' not in contact_info.keys()):
            raise KeyError("Contact record must include 'contact_id' or a name ('name' or 'last_name')")

        custom_fields = contact_info.pop('custom_fields', {})
        # Keys in contact_info need to be in CONTACT_PARAMS
        for key in contact_info.keys():
            if key not in self.CONTACT_PARAMS:
                raise KeyError("'%s' is not a valid parameter for Contact creation." % key)

        # To urlencode properly, the python dict key must be set to 'contact[<key>]'
        # _key_coded_dict() is designed to automate this process
        contact_param = _key_coded_dict({'contact': contact_info})
        for key, value in custom_fields.items():
            contact_param['contact[custom_fields][%s]' % key] = value
        url_params.update(contact_param)

        if contact_id is None:
            return self._post_data(url_noparam, url_params)
        else:
            return self._put_data(url_noparam, url_params)

    def create_contact(self, contact_info):
        """
        Creates a new contact based on contact_info

        ARGUMENTS

            contact_info - dict of fields (see CONTACT_PARAMS for valid field names)

        RESPONSE STRUCTURE

        see get_contact()
        """
        return self._upsert_contact(contact_info=contact_info, contact_id=None)

    def update_contact(self, contact_info, contact_id):
        """
        Edits contact with the unique base_id based on contact_info with fields shown in CONTACT_PARAMS.

        ARGUMENTS

            contact_info - dict of fields (see CONTACT_PARAMS for valid field names)
            contact_id - contact being updated

        RESPONSE STRUCTURE

        see get_contact()
        """
        return self._upsert_contact(contact_info=contact_info, contact_id=contact_id)

    def _unwrap_custom_fields(self, response):
        """
        Unwraps one level of indirection of custom field definitions
        """
        fields = {}
        for item in response:
            field = item['custom_field']
            if field['list_options']:
                field['list_options'] = dict(field['list_options'])
            fields[field['name']] = field
        return fields

    def get_contact_custom_fields(self, filterable=False):
        """
        Returns contact custom field definitions

        ARGUMENTS

            filterable - if True, return only fields marked as filterable

        RESPONSE STRUCTURE

        Note: for dropdown fields, list_options is a dict mapping option IDs
        to their values

        {'field name':
            {'custom_scope': ...
             'date_time': ...
             'field_type': ...
             'filterable': ...
             'for_contact': ...
             'for_organisation': ...
             'id': ...
             'list_options': ...
             'list_options_max': ...
             'name': ...
             'owner_id': ...
             'owner_type': ...
             'position': ...
             'settings': ...
             'value_editable_only_by_admin': ...
            },
        ...}
        """
        path = '/custom_fields'
        url_noparam = self._build_resource_url('crm', 1, path)
        url_params = {
            'filterable': str(filterable).lower(),
        }
        response = self._get_data(url_noparam, url_params)
        return self._unwrap_custom_fields(response)

    ##########################
    # Deals Functions and Constants
    ##########################
    def _build_deal_resource(self, deal_id=None, deal_ids=None, contact_ids=None, stage=None, page=1, per_page=None,
                             format=None):
        """
        Returns a tuple of URL (without parameters) and params to get deal objects meeting filter criteria

        ARGUMENTS

        Object or Parent Object (include only one)
            deal_id
            contact_id
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        RESPONSE STRUCTURE

        see get_deal()
        """
        url_params = dict()
        path = '/deals'

        if contact_ids is not None:
            # https://app.futuresimple.com/apis/sales/api/v2/contacts/deals.json?contact_ids=40905809
            url_params['contact_ids'] = contact_ids
            url_noparam = self._build_resource_url('sales', 2, '/contacts/deals', format)
        else:
            if stage is None:
                url_params['dont_scope_by_stage'] = 'true'
            elif stage in self.DEAL_STAGES:
                url_params['stage'] = stage
            else:
                raise ValueError("'%s' is not a valid stage, must come from '%s'" % str(stage),
                                 ','.join(self.DEAL_STAGES))

            if deal_id is not None:
                path += '/%d' % deal_id
            elif deal_ids is not None:
                # Used by all get() callers to increase standardization
                url_params['deal_ids'] = ','.join(str(x) for x in deal_ids)
            url_noparam = self._build_resource_url('sales', 1, path, format)

        url_params['page'] = page
        if per_page is not None:
            url_params['per_page'] = per_page

        return url_noparam, url_params

    def get_deals(self, deal_ids=None, page=1, stage=None):
        """
        Gets deal objects matching filter criteria.

        ARGUMENTS

            stage (default None) - the stage of deals to return (see DEAL_STAGES list for options)
            page (default 1) - the set of deals to return

        RESPONSE STRUCTURE

        see search_deals()
        """
        url_noparam, url_params = self._build_deal_resource(deal_ids=deal_ids, stage=stage, page=page)
        return self._get_data(url_noparam, url_params)

    def get_deal(self, deal_id):
        """
        Gets the deal with the given deal_id. Returns the deal info.
        """
        url_noparam, url_params = self._build_deal_resource(deal_ids=[deal_id])
        return self._get_data(url_noparam, url_params)

    def search_deals(self, filters=None, sort_by=None, sort_order='asc', tags_exclusivity='and', page=1):
        """
        Returns records for deals meeting the filter criteria and ordered by sort criteria, in batches of 20

        Native response structure:
        {'items':
            [{'deal':
                {'account_id': ...
                 'added_on': ...
                 'contact_ids': ...
                 'created_at': ...
                 'currency': ...
                 'deal_account': ...
                 'deal_tags': ...
                 'dropbox_email': ...
                 'entity_id': ...
                 'exchange_rate': ...
                 'hot': ...
                 'id': ...
                 'is_closed': ...
                 'is_new': ...
                 'last_stage_change_at': ...
                 'loss_reason_id': ...
                 'name': ...
                 'overdue_tasks': ...
                 'scope': ...
                 'sort_value': ...
                 'source_id': ...
                 'stage_code': ...
                 'stage_id': ...
                 'stage_name': ...
                 'unread_emails': ...
                 'updated_at': ...
                 'user_id': ...
                 'user_name': ...
                }
            }, ...],
        'success': ...
        'metadata': ...
        }
        """
        url_noparam = self._build_search_url('deal')

        valid_params = dict()
        valid_params['page'] = page

        # Handle stage separately because it requires extra validation
        if filters is None or 'stage' not in filters:
            valid_params['dont_scope_by_stage'] = True
        elif filters['stage'] is None:
            valid_params['dont_scope_by_stage'] = True
            del filters['stage']
        elif filters['stage'] in self.DEAL_STAGES:
            valid_params['stage'] = filters['stage']
            del filters['stage']
        else:
            raise ValueError('Stage must be absent, None, or a value from DEAL_STAGES.')

        # Handle other filters
        if filters is not None:
            for key, value in filters.items():
                if key in self.DEAL_FILTERS:
                    if key in ['tag_ids', 'tags']:
                        # tags are case sensitive
                        valid_params[key] = ','.join(value)
                        if tags_exclusivity in ['and', 'or']:
                            valid_params['tags_exclusivity'] = tags_exclusivity
                        else:
                            raise ValueError("tags_exclusivity must be 'and' or 'or'")
                    else:
                        # only lower case strings successfully match (regardless of original text case)
                        valid_params[key] = str(value).lower()
                else:
                    raise ValueError("%s is not a valid filter for a deal search" % key)

        # Configure sort order
        if sort_by is not None:
            if sort_by in self.DEAL_SORTS:
                valid_params['sort_by'] = sort_by
            else:
                raise ValueError("%s is not a valid sort field for a deal search" % sort_by)
            if sort_order in ['asc', 'desc']:
                valid_params['sort_order'] = sort_order
            else:
                raise ValueError("%s is not a valid sort order for a deal search" % sort_order)

        return self._get_data(url_noparam, valid_params)

    def _upsert_deal(self, deal_info=None, deal_id=None):
        """
        Updates or Inserts a deal

        ARGUMENTS

            deal_info - dict of fields (see DEAL_PARAMS for valid field names)
            deal_id (optional) - deal being updated (otherwise new deal will be created)

        RESPONSE STRUCTURE

        see get_deal()
        """
        url_noparam, url_params = self._build_deal_resource(deal_id=deal_id)

        # If we are creating a new deal, we must have name and entity_id parameters
        # and we always must have some parameter
        if deal_info is None or (deal_id is None and
                                ('name' not in deal_info.keys() or 'entity_id' not in deal_info.keys())):
            return "Missing required attributes 'name' or 'entity_id'"

        final_params = dict()
        custom_fields = deal_info.pop('custom_fields', {})
        for key in deal_info.keys():
            if key not in self.DEAL_PARAMS:
                return "%s is not a legal deal attribute" % key
            else:
                final_params[key] = deal_info[key]
        for key, value in custom_fields.items():
            final_params['custom_fields[%s]' % key] = value

        if deal_id is None:
            return self._post_data(url_noparam, final_params)
        else:
            return self._put_data(url_noparam, final_params)

    def create_deal(self, deal_info):
        """
        Creates a new deal based on deal_info

        ARGUMENTS

            deal_info - dict of fields (see CONTACT_PARAMS for valid field names)

        RESPONSE STRUCTURE

        see get_deal()
        """
        return self._upsert_deal(deal_info=deal_info)

    def update_deal(self, deal_info, deal_id):
        """
        Edits deal with the unique base_id based on deal_info with fields shown in CONTACT_PARAMS.

        ARGUMENTS

            deal_info - dict of fields (see CONTACT_PARAMS for valid field names)
            deal_id - deal being updated

        RESPONSE STRUCTURE

        see get_deal()
        """
        return self._upsert_deal(deal_info=deal_info, deal_id=deal_id)

    def get_deal_custom_fields(self, filterable=False):
        """
        Returns deal custom field definitions

        ARGUMENTS

            filterable - if True, return only fields marked as filterable

        RESPONSE STRUCTURE

        Note: for dropdown fields, list_options is a dict mapping option IDs
        to their values

        {'field name':
            {'custom_scope': ...
             'date_time': ...
             'field_type': ...
             'filterable': ...
             'id': ...
             'list_options': ...
             'list_options_max': ...
             'name': ...
             'owner_id': ...
             'owner_type': ...
             'position': ...
             'settings': ...
             'value_editable_only_by_admin': ...
             'writable': ...
            },
        ...}
        """
        path = '/deal_custom_fields'
        url_noparam = self._build_resource_url('sales', 1, path)
        url_params = {
            'filterable': str(filterable).lower(),
        }
        response = self._get_data(url_noparam, url_params)
        return self._unwrap_custom_fields(response)

    ##########################
    # Sources Functions
    ##########################
    SOURCES_VALUES = ['all', 'mine', 'auto']

    def _build_sources_resource(self, source_id=None, type='all', format=None):
        """
        Returns a tuple of URL (without parameters) and params to get source objects meeting filter criteria

        ARGUMENTS

        Object ID (do not combine with type):
            source_id - the ID of the source record
        Type (do not combine with source_id):
            type='all' (default) - list all sources, regardless of who created them
            type='mine' - only list sources created by authenticated user
            type='auto' - (unknown behavior)

        RESPONSE STRUCTURE

        see get_sources(), get_source()
        """
        path = '/sources'
        url_params = dict()

        if source_id is not None:
            path += '/%d' % source_id
        else:
            if type in self.SOURCES_VALUES:
                if type == 'all':
                    url_params['other'] = 1
                elif type == 'auto':
                    url_params['auto'] = 1
            else:
                raise ValueError("'type' was set to '%s', but must come from '%s'" % str(type),
                                 "', '".join(['all', 'mine', 'auto']))

        url_noparam = self._build_resource_url('sales', 1, path, format)
        return url_noparam, url_params

    def get_sources(self, type='auto'):
        """
        Get all records for sources (of deals) of the indicated type

        ARGUMENTS

        Type:
            type='all' (default) - list all sources, regardless of who created them
            type='mine' - only list sources created by authenticated user
            type='auto' - (unknown behavior)

        RESPONSE STRUCTURE

        [{'source':
            {'created_at': ...
             'id': ...
             'name': ...
             'permissions_holder_id': ...
             'updated_at': ...
             'user_id': ...
            }
        }, ...]
        """
        url_noparam, url_params = self._build_sources_resource(type=type)
        return self._get_data(url_noparam, url_params)

    def get_source(self, source_id):
        """
        Get record for source (of deals) indicated by source_id

        ARGUMENTS

            source_id - the ID of the source record

        RESPONSE STRUCTURE

        {'source':
            {'created_at': ...
             'id': ...
             'name': ...
             'permissions_holder_id': ...
             'updated_at': ...
             'user_id': ...
            }
        }
        """
        url_noparam, url_params = self._build_sources_resource(source_id=source_id)
        return self._get_data(url_noparam, url_params)

    ##########################
    # Lead Functions and Constants
    ##########################

    def _build_lead_resource(self, lead_id=None, page=None, per_page=None, format=None):
        """
        Returns a tuple of URL (without parameters) and params to get lead objects meeting filter criteria

        ARGUMENTS

        Object ID:
            lead_id -
        Format:
            format (default None) - see BaseAPIService._apply_format() for accepted values

        RESPONSE STRUCTURE

        see get_leads(), get_lead()
        """
        path = '/leads'
        url_params = dict()

        if lead_id is not None:
            path += '/%d' % lead_id
        if page is not None:
            url_params['page'] = page
        if per_page is not None:
            url_params['per_page'] = per_page

        url_noparam = self._build_resource_url('leads', 1, path, format)
        return url_noparam, url_params

    def get_leads(self, page=0, per_page=20):
        """
        Gets lead objects in batches of 20

        ARGUMENTS

            page - the set of leads to return. 0 (default) returns the first 20.

        RESPONSE STRUCTURE

        {'items':
            [{'lead':
                {'account_id': ...
                 'added_on': ...
                 'company_name': ...
                 'conversion_name': ...
                 'created_at': ...
                 'display_name': ...
                 'first_name': ...
                 'id': ...
                 'last_activity_date': ...
                 'last_name': ...
                 'owner_id': ...
                 'sort_value': ...
                 'state': ...
                 'user_id': ...
                }
              'success': ...
              'metatdata': ...
            }, ...],
         'success': ...
         'metadata': ...
        }
        """
        url_noparam, url_params = self._build_lead_resource(page=page, per_page=per_page)
        return self._get_data(url_noparam, url_params)

    def get_lead(self, lead_id):
        """
        Gets the lead with the given lead_id

        ARGUMENTS

            lead_id - the ID of a lead

        RESPONSE STRUCTURE

        {'lead':
            {'first_name': ...
             'last_name': ...
             'user_id': ...
             'account_id': ...
             'sort_value': ...
             'created_at': ...
             'last_activity_date': ...
             'conversion_name': ...
             'state': ...
             'company_name': ...
             'display_name': ...
             'id': ...
             'added_on': ...
             'owner_id': ...
            }
          'success': ...
          'metatdata': ...
        }
        """
        url_noparam, url_params = self._build_lead_resource(lead_id=lead_id)
        return self._get_data(url_noparam, url_params)

    def search_leads(self, filters=None, sort_by=None, sort_order='asc', tags_exclusivity='and', page=0, per_page=20):
        """
        Returns records for leads meeting the filter criteria and ordered by sort criteria, in batches

        ARGUMENTS

        Paging:
            page (default 0) - the set of leads to return
            per_page - the number of objects listed on each page

        RESPONSE STRUCTURE

        {'items':
            [{'lead':
                {'first_name': ...
                 'last_name': ...
                 'user_id': ...
                 'account_id': ...
                 'sort_value': ...
                 'created_at': ...
                 'last_activity_date': ...
                 'conversion_name': ...
                 'state': ...
                 'company_name': ...
                 'display_name': ...
                 'id': ...
                 'added_on': ...
                 'owner_id': ...
                }
              'success': ...
              'metatdata': ...
            }, ...],
         'success': ...
         'metadata': ...
        }
        """
        url_noparam = self._build_search_url('lead')
        valid_params = dict()

        valid_params['page'] = page
        valid_params['per_page'] = per_page

        if filters is not None:
            for key, value in filters.items():
                if key in self.LEAD_FILTERS:
                    if key in ['tag_ids', 'tags']:
                        # tags are case sensitive
                        valid_params[key] = ','.join(value)
                        if tags_exclusivity in ['and', 'or']:
                            valid_params['tags_exclusivity'] = tags_exclusivity
                        else:
                            raise ValueError("tags_exclusivity must be 'and' or 'or'")
                    else:
                        # only lower case strings successfully match (regardless of original text case)
                        valid_params[key] = str(value).lower()
                else:
                    raise ValueError("%s is not a valid filter for a Lead search" % key)

        if sort_by is not None:
            if sort_by in self.LEAD_SORTS:
                valid_params['sort_by'] = sort_by
            else:
                raise ValueError("%s is not a valid sort field for a Lead search" % sort_by)
            if sort_order in ['asc', 'desc']:
                valid_params['sort_order'] = sort_order
            else:
                raise ValueError("%s is not a valid sort order for a Lead search" % sort_order)

        return self._get_data(url_noparam, valid_params)

    def _upsert_lead(self, lead_info=None, lead_id=None):
        """
        Updates or Inserts a lead

        ARGUMENTS

            lead_info - dict of fields (see DEAL_PARAMS for valid field names)
            lead_id (optional) - lead being updated (otherwise new lead will be created)

        RESPONSE STRUCTURE

        see get_lead()
        """
        url_noparam, url_params = self._build_lead_resource(lead_id=lead_id)

        # If we are creating a new lead, we must have name and entity_id parameters
        # and we always must have some parameter
        if lead_info is None or (lead_id is None and 'last_name' not in lead_info.keys() and
                                 'company_name' not in lead_info.keys()):
            raise KeyError("Lead record must include 'lead_id' or a name ('last_name' or 'company_name')")

        lead_params = dict()
        custom_fields = lead_info.pop('custom_fields', {})
        for key in lead_info.keys():
            if key not in self.LEAD_PARAMS:
                raise KeyError("'%s' is not a legal lead attribute" % key)
            else:
                lead_params[key] = lead_info[key]
        lead_params = _key_coded_dict({'lead': lead_params})
        for key, value in custom_fields.items():
            lead_params['lead[custom_field_values][%s]' % key] = value
        url_params.update(lead_params)

        if lead_id is None:
            return self._post_data(url_noparam, url_params)
        else:
            return self._put_data(url_noparam, url_params)

