__author__ = 'Clayton Daley'

import logging
logger = logging.getLogger(__name__)

import json
import requests
from authentication import Password, Token
from prototypes import Resource, Collection


def _unicode_dict(d):
    new_dict = dict()
    for k, v in d.iteritems():
        new_dict[k] = unicode(v).encode('utf-8')
    return new_dict


def create_from_token(token, debug=False):
    auth = Token(token)
    api = BaseAPI(auth)
    api.debug = debug
    return api


def create_from_password(username, password, debug=False):
    auth = Password(username, password)
    api = BaseAPI(auth)
    api.get_token(username, password)
    api.debug = debug
    return api


class BaseAPI(object):
    """
    The BaseAPI class is a Mediator that knows how to combine authentication an entity objects to achieve specific API
    actions (get, put, post, delete).  It also knows how to handle a variety of common API endpoint errors.
    """
    debug = False

    def __init__(self, auth):
        self.auth = auth

    def get(self, entity):
        if not isinstance(entity, Resource):
            TypeError("Must submit Resource to get()")

        logger.debug("Preparing GET with:")
        logger.debug("url:  %s" % entity.URL(self.debug))
        logger.debug("headers:  %s" % self.auth.headers(entity.API_VERSION))
        response = requests.get(url=entity.URL(self.debug), headers=self.auth.headers(entity.API_VERSION))

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("GET SUCCESS:  %s" % response.text)
            entity.set_data(response.json()['data'])
        else:
            print("GET ERROR:  %s" % response.text)
        # entity is mutable, but this simplifies chaining and assignment
        return entity

    def save(self, entity):
        if not isinstance(entity, Resource):
            raise TypeError("Can only save() a Resource")
        if entity.id is None:
            raise ValueError("ID must be set to save(), use create() instead")

        data = {'data': entity.params()}
        if len(data) == 0:
            raise ValueError("No data to save.")

        headers = self.auth.headers(entity.API_VERSION)
        headers['Content-Type'] = 'application/json'

        logger.debug("Preparing PUT with:")
        logger.debug("url:  %s" % entity.URL(self.debug))
        logger.debug("headers:  %s" % headers)
        logger.debug("data:  %s" % data)
        response = requests.put(url=entity.URL(self.debug), headers=headers, data=json.dumps(data))

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("PUT:  %s" % response.text)
            entity.set_data(response.json()['data'])
        else:
            print("PUT ERROR:  %s" % response.text)
        # entity is mutable, but this simplifies chaining and assignment
        return entity

    def create(self, entity):
        if not isinstance(entity, Resource):
            raise TypeError("Can only create() a Resource")
        if entity.id is not None:
            raise ValueError("Contact already exists, use save() instead of create()")

        data = {'data': entity.params()}
        if len(data) == 0:
            raise ValueError("No data to save.")

        headers = self.auth.headers(entity.API_VERSION)
        headers['Content-Type'] = 'application/json'

        logger.debug("Preparing POST with:")
        logger.debug("url:  %s" % entity.URL(self.debug))
        logger.debug("headers:  %s" % headers)
        logger.debug("data:  %s" % data)
        response = requests.post(url=entity.URL(self.debug), headers=headers, data=json.dumps(data))

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("POST SUCCESS:  %s" % response.text)
            entity.set_data(response.json()['data'])
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
        # Add page, per_page, and order_by to params
        params = entity.params()
        params['page'] = page
        params['per_page'] = per_page

        # clean up boolean formatting
        for k, v in params.iteritems():
            if isinstance(params[k], bool):
                if params[k]:
                    params[k] = 'true'
                else:
                    params[k] = 'false'

        logger.debug("Preparing GET with:")
        logger.debug("url:  %s" % entity.URL(self.debug))
        logger.debug("headers:  %s" % headers)
        logger.debug("params:  %s" % params)

        if order_by is not None:
            if order_by not in entity.ORDERS:
                raise ValueError('%s is not a valid sort order for %s' % order_by, entity.__class__.__name__)
            params['order_by'] = order_by

        response = requests.get(url=url, params=params, headers=headers)

        if requests.codes.multiple_choices > response.status_code >= requests.codes.ok:
            print("GET SUCCESS:  %s" % response.text)
            return entity.format_page(response.json()['items'])
        else:
            print("GET ERROR:  %s" % response.text)

