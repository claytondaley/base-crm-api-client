__author__ = 'Clayton Daley'

import logging
logger = logging.getLogger(__name__)

import collections
import base_client
from pprint import pformat
from darts.lib.utils.lru import SynchronizedLRUDict

DEFAULT_CACHE = 1


class Feed(collections.Sequence):
    log = logger.info
    PAGE_SIZE = 20  # must match the built-in behavior of the feed API call

    def __init__(self, conn, type=None, cache=DEFAULT_CACHE):
        self.conn = conn
        self.type = type
        # Store string in URL used to access specific pages
        self.pages = ['null']  # Ensure index and pages match
        self.cache = SynchronizedLRUDict(cache)
        self.page_0 = None
        try:
            self.get_page(0)
        except IndexError:
            # Empty first page isn't a problem
            pass

    def __getitem__(self, item):
        """
        In a Sequence, iteration is achieved by making repeated calls to self[i] so this function implements all of the
        key logic in the class including the basis for iteration.

        For loops expect that an IndexError will be raised for illegal indexes to allow proper detection of the end of
        the sequence.
        """
        self.log("Getting Item %d" % item)
        page = item // self.PAGE_SIZE
        loc = item % self.PAGE_SIZE
        page = self.get_page(page)
        return page[loc]

    def __len__(self):
        return sum([1 for _ in self])  # Consider optimizing using paging logic

    def get_page(self, page):
        if page in self.cache:
            return self.cache[page]
        elif page == 0 and self.page_0 is not None:
            return self.page_0
        elif len(self.pages) < page + 1:
            while len(self.pages) < page:
                self.get_page(len(self.pages))
        elif self.pages[page] == 'End':
            # Per code below, this marks an empty page.  None was not used because the API functions will interpret
            # None as a request for the first page (if the value was ever accidentally sent through).
            self.log("Page is end, raising IndexError")
            raise IndexError("list index out of range")

        self.log("Loading page with timestamp %s" % self.pages[page])

        # Load page using timestamp stored in pages()
        feed_page = self.get_feed(self.pages[page])

        # Check for bad response
        if not feed_page or 'success' not in feed_page or not feed_page['success']:
            raise BaseException("An API request failed, returning:\n%s" % pformat(feed_page))

        # Store next page in pages table
        if self.pages[page] == feed_page['metadata']['timestamp'] or len(feed_page['items']) < self.PAGE_SIZE:
            # This is the last page so leave a breadcrumb in the pages table.  None was not used because the API
            # functions will interpret None as a request for  the first page (if the value was ever accidentally sent
            # through).
            next_page = 'End'
        else:
            next_page = feed_page['metadata']['timestamp']
        if len(self.pages) > page + 1:
            # Next page is already in table, verify that it is what we expect
            if self.pages[page + 1] != next_page:
                raise BaseException("Invalid State:  Reference to next page has changed since page was last processed.")
        else:
            # Next page is not in table, append
            assert len(self.pages) == page + 1
            self.pages.append(next_page)
            assert len(self.pages) == page + 2

        # Extract and return feed content
        if len(feed_page['items']) == 0:
            # This is an empty page so leave a breadcrumb in the pages table.  None was not used because the API
            # functions will interpret None as a request for  the first page (if the value was ever accidentally sent
            # through).
            self.pages[page] = 'End'
            self.log("No items, raising IndexError")
            raise IndexError("list index out of range")
        else:
            self.cache[page] = feed_page['items']
            return feed_page['items']

    def get_feed(self, timestamp):
        """
        This function makes it easy for subclasses to send different parameters to the underlying API call without
        duplicating any of the the paging logic.
        """
        return self.conn._get_feed(type=self.type, timestamp=timestamp, format=self.conn.format)


class ContactFeed(Feed):
    def __init__(self, conn, contact_id, type=None, cache=DEFAULT_CACHE):
        self.contact_id = contact_id
        Feed.__init__(self, conn=conn, type=type, cache=cache)

    def get_feed(self, timestamp):
        return self.conn._get_feed(contact_id=self.contact_id, type=self.type, timestamp=timestamp,
                                   format=self.conn.format)


class ContactEmailFeed(ContactFeed):
    def __init__(self, conn, contact_id, cache=DEFAULT_CACHE):
        ContactFeed.__init__(self, conn=conn, contact_id=contact_id, type='Email', cache=cache)


class ContactNoteFeed(ContactFeed):
    def __init__(self, conn, contact_id, cache=DEFAULT_CACHE):
        ContactFeed.__init__(self, conn=conn, contact_id=contact_id, type='Note', cache=cache)


class ContactCallFeed(ContactFeed):
    def __init__(self, conn, contact_id, cache=DEFAULT_CACHE):
        ContactFeed.__init__(self, conn=conn, contact_id=contact_id, type='Call', cache=cache)


class ContactTaskFeed(ContactFeed):
    def __init__(self, conn, contact_id, cache=DEFAULT_CACHE):
        ContactFeed.__init__(self, conn=conn, contact_id=contact_id, type='Task', cache=cache)


# Leads
class LeadFeed(Feed):
    def __init__(self, conn, lead_id, type=None, cache=DEFAULT_CACHE):
        self.lead_id = lead_id
        Feed.__init__(self, conn=conn, type=type, cache=cache)

    def get_feed(self, timestamp):
        return self.conn._get_feed(lead_id=self.lead_id, type=self.type, timestamp=timestamp,
                                   format=self.conn.format)


class LeadEmailFeed(LeadFeed):
    def __init__(self, conn, lead_id, cache=DEFAULT_CACHE):
        LeadFeed.__init__(self, conn=conn, lead_id=lead_id, type='Email', cache=cache)


class LeadNoteFeed(ContactFeed):
    def __init__(self, conn, lead_id, cache=DEFAULT_CACHE):
        LeadFeed.__init__(self, conn=conn, lead_id=lead_id, type='Note', cache=cache)


class LeadCallFeed(ContactFeed):
    def __init__(self, conn, lead_id, cache=DEFAULT_CACHE):
        LeadFeed.__init__(self, conn=conn, lead_id=lead_id, type='Call', cache=cache)


class LeadTaskFeed(ContactFeed):
    def __init__(self, conn, lead_id, cache=DEFAULT_CACHE):
        LeadFeed.__init__(self, conn=conn, lead_id=lead_id, type='Task', cache=cache)


class BaseObjectFactory(object):
    """
    While most requests to the BaseCRM API are clearly stateless, some require that the client maintain information
    between calls.
    """
    def __init__(self, connection=None, token=None, email=None, password=None):
        if connection is not None:
            self.conn = connection
        elif token is not None:
            self.conn = base_client.BaseAPIService(token=token)
        elif email is not None and password is not None:
            self.conn = base_client.BaseAPIService(email=email, password=password)
        else:
            raise ValueError("Must provide a connection, token, or username/password.")

    def get_iterator_for_contact_feed(self, contact):
        pass

    def get_iterator_for_contact_emails(self, contact):
        pass