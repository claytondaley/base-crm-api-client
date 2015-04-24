#!/usr/bin/env python
"""Implements clients BaseCRM's APIs"""

import logging

logger = logging.getLogger(__name__)

import json
import requests
from v2.authentication import Password, Token
from prototype import Resource, Collection

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


def _unicode_dict(d):
    new_dict = dict()
    for k, v in d.iteritems():
        new_dict[k] = unicode(v).encode('utf-8')
    return new_dict


def create_from_token(token, debug=False):
    auth = Token(token)
    api = Rest(auth)
    api.debug = debug
    return api


def create_from_password(username, password, debug=False):
    auth = Password(username, password)
    api = Rest(auth)
    api.get_token(username, password)
    api.debug = debug
    return api


class Rest(object):
    """
    The BaseAPI class is a Mediator that knows how to combine authentication an entity objects to achieve specific API
    actions (get, put, post, delete).  It also knows how to handle a variety of common API endpoint errors.
    """
    debug = False

    def __init__(self, auth):
        self.auth = auth

    def get(self, entity):
        if not isinstance(entity, Resource):
            raise TypeError("Can only get() a Resource")

        logger.debug("Preparing GET with:")
        logger.debug("url:  %s" % entity.URL(self.debug))
        logger.debug("headers:  %s" % self.auth.headers(entity.API_VERSION))
        response = requests.get(url=entity.URL(self.debug), headers=self.auth.headers(entity.API_VERSION))

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("GET SUCCESS:  %s" % response.text)
            entity.set_data(response.json()[entity.DATA_PARENT_KEY])
        else:
            print("GET ERROR:  %s" % response.text)
        # entity is mutable, but this simplifies chaining and assignment
        return entity

    def save(self, entity):
        if not isinstance(entity, Resource):
            raise TypeError("Can only save() a Resource")
        if entity.id is None:
            raise ValueError("ID must be set to save(), use create() instead")

        data = entity.get_data()
        if len(data) == 0:
            raise ValueError("No data to save()")
        # Wrap the item in the relevant key
        data = {entity.DATA_PARENT_KEY: data}

        headers = self.auth.headers(entity.API_VERSION)
        headers['Content-Type'] = 'application/json'

        logger.debug("Preparing PUT with:")
        logger.debug("url:  %s" % entity.URL(self.debug))
        logger.debug("headers:  %s" % headers)
        logger.debug("data:  %s" % data)
        response = requests.put(url=entity.URL(self.debug), headers=headers, data=json.dumps(data))

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("PUT SUCCESS:  %s" % response.text)
            entity.set_data(response.json()[entity.DATA_PARENT_KEY])
        else:
            print("PUT ERROR:  %s" % response.text)
        # entity is mutable, but this simplifies chaining and assignment
        return entity

    def create(self, entity):
        if not isinstance(entity, Resource):
            raise TypeError("Can only create() a Resource")
        if entity.id is not None:
            raise ValueError("Contact already exists, use save() instead of create()")

        data = entity.get_data()
        if len(data) == 0:
            raise ValueError("No data for create()")
        # Wrap the item in the relevant key
        data = {entity.DATA_PARENT_KEY: data}

        headers = self.auth.headers(entity.API_VERSION)
        headers['Content-Type'] = 'application/json'

        logger.debug("Preparing POST with:")
        logger.debug("url:  %s" % entity.URL(self.debug))
        logger.debug("headers:  %s" % headers)
        logger.debug("data:  %s" % data)
        response = requests.post(url=entity.URL(self.debug), headers=headers, data=json.dumps(data))

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("POST SUCCESS:  %s" % response.text)
            entity.set_data(response.json()[entity.DATA_PARENT_KEY])
        else:
            print("POST ERROR:  %s" % response.text)
        # entity is mutable, but this simplifies chaining and assignment
        return entity

    def delete(self, entity):
        if not isinstance(entity, Resource):
            raise TypeError("Can only delete() a Resource")
        if entity.id is None:
            raise ValueError("ID must be set to delete()")

        response = requests.delete(url=entity.URL(self.debug), headers=self.auth.headers(entity.API_VERSION))
        logger.debug("Response:  \n%s" % response.text)

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("DELETE SUCCESS:  %s" % response.text)
        else:
            print("DELETE ERROR:  %s" % response.text)
        # entity is mutable, but this simplifies chaining and assignment
        return entity

    def get_page(self, entity, page, per_page=20, order_by=None):
        if not isinstance(entity, Collection):
            raise TypeError("Can only loadpage() for a Collection")

        url = entity.URL(self.debug)
        headers = self.auth.headers(entity.API_VERSION)
        # Add page, per_page, and order_by to format_data_get
        data = entity.format_data_set()
        data['page'] = page
        data['per_page'] = per_page

        # clean up boolean formatting
        for k, v in data.iteritems():
            if isinstance(data[k], bool):
                if data[k]:
                    data[k] = 'true'
                else:
                    data[k] = 'false'

        logger.debug("Preparing GET with:")
        logger.debug("url:  %s" % entity.URL(self.debug))
        logger.debug("headers:  %s" % headers)
        logger.debug("format_data_get:  %s" % data)

        if order_by is not None:
            if order_by not in entity.ORDERS:
                raise ValueError('%s is not a valid sort order for %s' % order_by, entity.__class__.__name__)
            data['order_by'] = order_by

        response = requests.get(url=url, params=data, headers=headers)

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("GET SUCCESS:  %s" % response.text)
            return entity.format_page(response.json()['items'])
        else:
            print("GET ERROR:  %s" % response.text)


class Sync(object):
    """
    Sync client...
    """
    def __init__(self, repository):
        self.repository = repository

    def sync(self):
        pass