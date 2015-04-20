from copy import deepcopy
import requests

__author__ = 'Clayton Daley'

import logging
logger = logging.getLogger(__name__)

import abc
import sys


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

    def headers(self, version):
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
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token,
        }
        headers = {
            # APP_ID: APP_SECRET
        }

        logger.debug("Preparing POST with:")
        logger.debug("url:  %s" % url)
        logger.debug("params:  %s" % params)
        logger.debug("headers:  %s" % headers)
        response = requests.post(url=url, params=params, headers=headers)
        logger.debug("Password response:\n%s" % response.text)
        self._access_token = response.json()['access_token']
        self._refresh_token = response.json()['refresh_token']


class Entity(object):
    """
    Makes it easy to check if an object is a BaseCRM Entity
    """
    def URL(self, debug):
        obj = self.__dict__

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

    def __init__(self, entity_id=None):
        if entity_id is not None and not isinstance(entity_id, int):
            raise TypeError("entity_id must be None or int")
        super(Resource, self).__init__()
        self.data = dict()
        self.dirty = dict()
        self.loaded = False
        # This way, entity.id will never tell the user to call get()
        self.data['id'] = entity_id
        self.__initialized = True

    def __setattr__(self, key, value):
        # If the __initialized flag isn't set yet, set the attribute normally
        if not '_Resource__initialized' in self.__dict__:
            self.__dict__[key] = value
            return
        if key in self.PROPERTIES:
            # If PROPERTIES contains a dict, this is a list of rules with which the value must comply
            if isinstance(self.PROPERTIES[key], dict):
                rules = self.PROPERTIES[key]
                # the 'type' key (optionally a list) contains all accepted types
                if 'type' in rules:
                    type = rules['type']
                    if not isinstance(rules, list):
                        type = [type]
                    if value.__class__ not in type:
                        raise TypeError("%s is not a valid type for %s" % value, key)
                # the 'in' key is a list of all acceptable values
                if 'in' in rules and value not in rules['in']:
                    raise ValueError("%s is not a valid value for #s" % value, key)
            # Otherwise, the PROPERTIES value is just the accepted type
            elif not isinstance(value, self.PROPERTIES[key]):
                raise TypeError("%s must be of type %s" % (key, self.PROPERTIES[key].__name__))
            self.dirty[key] = value
        elif '_%s' % key in self.PROPERTIES:
            raise KeyError("%s is readonly for %s" % (key, self.__class__.__name__))
        else:
            raise AttributeError("%s is not a valid attribute for %s" % (key, self.__class__.__name__))

    def __getattr__(self, key):
        # If the value has been set locally, it will be found in dirty and may be returned
        if key in self.dirty:
            return self.dirty[key]
        # 'id' must always return, either from data (where it is usually set) or None (thanks to PROPERTIES checks)
        if key != 'id' and not self.loaded:
            raise ReferenceError("Object has not been loaded. Use get() to populate data before requesting %s." % key)
        if key in self.data:
            return self.data[key]
        # Acknowledge property is valid by returning None
        if key in self.PROPERTIES:
            return None
        # Acknowledge readonly property is valid by returning None
        if "_%s" % key in self.PROPERTIES:
            return None
        raise AttributeError("%s not a valid attribute of %s" % (key, self.__class__.__name__))

    def set_data(self, data):
        # Assign actual data to self
        self.__dict__['data'] = self.format_data(data)
        # Mark data as loaded
        self.__dict__['loaded'] = True
        # Clear out dirty data
        self.__dict__['dirty'] = dict()

    def format_data(self, data):
        """
        This function exists to support custom formatting of data objects Address
        """
        return data  # data is mutable, but this simplifies inline assignment

    def params(self):
        params = deepcopy(self.dirty)
        # If needed, ID is encoded in URL
        return params


class ResourceV1(Resource):
    API_VERSION = 1
    # Needs a different URL builder
    @property
    def PATH(self, entity):
        url = 'https://app.futuresimple.com/apis/%s/api/v%d%s.json' % (self.RESOURCE, self.API_VERSION, self._PATH)


class Collection(Entity):
    """
    Entity is the base class for standard BaseCRM API Client entities.
    """
    API_VERSION = 2

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

    def params(self):
        params = deepcopy(self.filters)
        # If needed, ID is encoded in URL
        return params

    def format_data(self, data):
        # Return a page containing API data processed into Resources and Collections
        page = list()
        for record in data:
            entity = self._ITEM()
            entity.set_data(record['data'])
            page.append(entity)
        return page


class CollectionV1(Collection):
    """
    Tweaks various functions for old v1 resource structure
    """
    @property
    def PATH(self, entity):
        if type == 'contact':
            url, params = self._build_contact_resource()
        elif type == 'deal':
            url, params = self._build_deal_resource()
        elif type == 'lead':
            url, params = self._build_lead_resource()
        else:
            raise ValueError("Invalid search type.")
        return url + '/search.json'
