#!/usr/bin/env python
"""Provides interfaces and prototypes for BaseAPI components"""

import logging
from pprint import pformat

logger = logging.getLogger(__name__)

import abc
from copy import deepcopy
import requests
import sys

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


def _key_coded_dict(d):
    new_dict = dict()
    for k, v in d.iteritems():
        if isinstance(d, dict):
            for k2, v2 in v.iteritems():
                new_dict['%s[%s]' % k, k2] = v2
        else:
            new_dict[k] = v
    return new_dict


class IBaseCrmAuthentication(object):
    @abc.abstractmethod
    def headers(self):
        """
        Generate a string for
        :return: array
        """
        raise NotImplementedError("No implementation for %s in class %s" %
                                  (sys._getframe().f_code.co_name, self.__class__.__name__))


class BaseCrmAuthentication(IBaseCrmAuthentication):
    def __init__(self):
        self._access_token = None
        self._refresh_token = None

    def headers(self, version=2):
        if version == 1:
            return {
                'X-Pipejump-Auth': self._access_token,
                'X-Futuresimple-Token': self._access_token
            }
        elif version == 2:
            return {
                'Accept': 'application/json',
                'Authorization': 'Bearer %s' % self._access_token,
            }

    def refresh(self):
        if self._refresh_token is None:
            raise ReferenceError("Refresh key not available.")

        url = "https://api.getbase.com/oauth2/token"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token,
        }
        headers = {
            # APP_ID: APP_SECRET
        }

        logger.debug("Preparing POST with:")
        logger.debug("url:  %s" % url)
        logger.debug("format_data_get:  %s" % data)
        logger.debug("headers:  %s" % headers)
        response = requests.post(url=url, params=data, headers=headers)
        logger.debug("Password response:\n%s" % response.text)
        self._access_token = response.json()['access_token']
        self._refresh_token = response.json()['refresh_token']


class Entity(object):
    """
    Makes it easy to check if an object is a BaseCRM Entity
    """
    def URL(self, debug=False):
        if debug:
            url = 'https://api.sandbox.getbase.com'
        else:
            url = 'https://api.getbase.com'

        if isinstance(self, Resource) and self.id is not None:
            url += "/v%d/%s/%s" % (self.API_VERSION, self._PATH, self.id)
        else:
            url += "/v%d/%s" % (self.API_VERSION, self._PATH)
        return url


class Resource(Entity):
    """
    Entity is the base class for standard BaseCRM API Client entities.
    """
    API_VERSION = 2
    """
    This is the top-level key for arrays sent to and received from the API.  This must be done because APIv1 responses
    use a key that's specific to the response type.  For example, an APIv1 contact response is:

        {
            'contact': {
                'name': ...
                ...
                }
        }

    Even though APIv2 standardizes on 'data', an APIv2 Entity must process a response like:

        {
            'data': {
                'name': ...
                ...
                }
        }
    """
    DATA_PARENT_KEY = 'data'

    def __init__(self, entity_id=None):
        if entity_id is not None and not isinstance(entity_id, int):
            raise TypeError("entity_id must be None or int")
        super(Resource, self).__init__()
        self._data = dict()
        self._dirty = dict()
        self._loaded = False
        # This way, entity.id will never tell the user to call get()
        self._data['id'] = entity_id
        self.__initialized = True

    def __setattr__(self, key, value):
        """Enforce business rules on attributes and store them in a special location"""
        if not '_Resource__initialized' in self.__dict__:
            # If the __initialized flag isn't set yet, set the attribute normally
            object.__setattr__(self, key, value)
            return self
        if key in self._dirty:
            # Must nest because we don't want to check _data if a non-matching value is in _dirty
            if value is self._dirty['key']:
                # Compare using 'is' to ensure mutability is preserved, in which case we don't need to update
                return self
        elif key in self._data and value is self._data['key']:
            # Compare using 'is' to ensure mutability is preserved, in which case we don't need to update
            return self
        if key in self.PROPERTIES:
            # PROPERTIES contains a dict -- a list of key-value pairs describing an attributes (PROPERTIES key) and the
            # business rules that apply to its value (PROPERTIES value)
            if isinstance(self.PROPERTIES[key], dict):
                rules = self.PROPERTIES[key]
                # the 'type' key (optionally a list) contains all accepted types
                if 'type' in rules:
                    # Get acceptable types and make sure they're in a list
                    type_ = rules['type']
                    if not isinstance(type_, list):
                        type_ = [type_]
                    match = False
                    for t in type_:
                        if isinstance(value, t):
                            match = True
                            break
                    if not match:
                        raise TypeError("%s is not a valid type for %s.%s" % (value, self.__class__.__name__, key))
                # the 'in' key is a list of all acceptable values
                if 'in' in rules and value not in rules['in']:
                    raise ValueError("%s is not a valid value for %s.%s" % (value, self.__class__.__name__, key))
            # Otherwise, the PROPERTIES value is just the accepted type
            elif not isinstance(value, self.PROPERTIES[key]):
                raise TypeError("%s.%s must be of type %s" % (self.__class__.__name__, key, self.PROPERTIES[key].__name__))
            self._dirty[key] = value
            return self
        elif '_%s' % key in self.PROPERTIES:
            raise KeyError("%s is readonly for %s" % (key, self.__class__.__name__))
        else:
            raise AttributeError("%s is not a valid attribute for %s" % (key, self.__class__.__name__))

    def __getattr__(self, key):
        # If the value has been set locally, it will be found in dirty and may be returned
        if key == '__deepcopy__':
            return object.__deepcopy__
        if key in self._dirty:
            return self._dirty[key]
        # 'id' must always return, either from data (where it is usually set) or None (thanks to PROPERTIES checks)
        if key != 'id' and not self._loaded:
            raise ReferenceError("Object has not been loaded. Use get() to populate data before requesting %s." % key)
        if key in self._data:
            return self._data[key]
        # Acknowledge property is valid by returning None
        if key in self.PROPERTIES:
            return None
        # Acknowledge readonly property is valid by returning None
        if "_%s" % key in self.PROPERTIES:
            return None
        raise AttributeError("%s not a valid attribute of %s" % (key, self.__class__.__name__))

    def set_data(self, data):
        """
        Sets the local object to the values indicated in the 'data' array. This function uses the helper
        format_data_set() to allow objects to, for example, convert elements of the response into more usable types.
        For more information on this process, see format_data_set().
        """
        # Assign actual data to self
        self.__dict__['_data'] = self.format_data_set(data)
        # Mark data as loaded
        self.__dict__['loaded'] = True
        return self  # returned for setting and chaining convenience

    def format_data_set(self, data):
        """
        Objects should overload this function to adjust the input, including converting elements into custom types.
        For example,

         - The v2 Contact object wraps the address up into an Address object
         - In v1, tags are sent as comma-separated lists that should be exploded into real lists
        """
        return data  # returned for setting and chaining convenience

    def get_data(self):
        data = self.format_data_get(deepcopy(self._dirty))
        # If needed, ID is encoded in URL
        return {self.DATA_PARENT_KEY: data}

    def format_data_get(self, dirty):
        data = deepcopy(dirty)
        # If needed, ID is encoded in URL
        return data


class ResourceV1(Resource):
    API_VERSION = 1
    # Needs a different URL builder

    def URL(self, debug=False):
        if debug:
            raise ValueError("BaseCRM's v1 API does not support debug mode.")

        url = 'https://app.futuresimple.com/apis/%s/api/v%d/%s' % (self.RESOURCE, self.API_VERSION, self._PATH)
        if self.id is not None:
            url += '/%d' % self.id
        return url + '.json'

    def get_data(self):
        dirty = self.format_data_get(deepcopy(self._dirty))

        data = {
            self.DATA_PARENT_KEY: dirty
            # e.g. 'contact': {'name': ...}
        }

        # to generate ?contact[name]=...
        return _key_coded_dict(data)


class Collection(Entity):
    """
    Entity is the base class for standard BaseCRM API Client entities.
    """
    API_VERSION = 2

    @property
    def _PATH(self):
        return self._ITEM._PATH

    def __init__(self, **kwargs):
        self.__dict__['filters'] = dict()
        for key, value in kwargs:
            self.key = value

    def __setattr__(self, key, value):
        # If the __initialized flag isn't set yet, set the attribute normally
        if key in self.FILTERS:
            # Arrays list acceptable values
            if isinstance(self.FILTERS[key], list) and value in self.FILTERS[key]:
                raise ValueError("%s is not a valid filter value for #s" % value, key)
            if not isinstance(value, self.PROPERTIES[key]):
                raise TypeError("%s must be of type %s" % (key, self.FILTERS[key].__name__))
            self.filters[key] = value
        else:
            raise AttributeError("%s is not a valid filter for %s" % (key, self.__class__.__name__))

    def get_data(self):
        data = deepcopy(self.filters)
        # If needed, ID is encoded in URL
        return data

    def format_page(self, data):
        # Return a page containing API data processed into Resources and Collections
        page = list()
        for record in data:
            entity = self._ITEM()
            entity.set_data(record)
            page.append(entity)
        return page


class CollectionV1(Collection):
    """
    Tweaks various functions for old v1 resource structure
    """
    def URL(self, debug=False):
        if debug:
            raise ValueError("BaseCRM's v1 API does not support debug mode.")

        url = 'https://app.futuresimple.com/apis/%s/api/v%d/%s' % (self.RESOURCE, self.API_VERSION, self._PATH)
        return url + '/search.json'

    def format_data_set(self):
        data = {
            self.RESPONSE_KEY: deepcopy(self.filters)
            # e.g. 'contact': {'name': ...}
        }

        # to generate ?contact[name]=...
        return _key_coded_dict(data)
