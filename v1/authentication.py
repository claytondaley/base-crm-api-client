#!/usr/bin/env python
"""Implements Authentication options for BaseCRM's v1 API"""

import logging
logger = logging.getLogger(__name__)

import requests
from prototype import BaseCrmAuthentication, AuthenticationError

__author__ = 'Clayton Daley III'
__copyright__ = "Copyright 2015, Clayton Daley III"
__license__ = "Apache License 2.0"
__version__ = "2.0.0"
__maintainer__ = "Clayton Daley III"
__status__ = "Development"


class Authentication(BaseCrmAuthentication):
    def headers(self):
        return {
            'X-Pipejump-Auth': self._access_token,
            'X-Futuresimple-Token': self._access_token
        }

    def refresh(self):
        raise AuthenticationError("APIv1 Authentication objects cannot refresh.")


class Password(Authentication):
    def __init__(self, username, password):
        """
        Authenticate with an email and password

        Keyword arguments;
        email -- user's BaseCRM email
        password -- user's BaseCRM password
        """
        super(Password, self).__init__()

        data = {
            'username': username,
            'password': password,
        }
        url = "https://sales.futuresimple.com/api/v1/authentication.json"

        logger.debug("Preparing POST with:")
        logger.debug("url:  %s" % url)
        logger.debug("format_data_get:  %s" % data)
        response = requests.post(url=url, data=data)
        logger.debug("APIv1 password response:\n%s" % response.text)
        if 'token' not in response.json()['authentication']:
            raise AuthenticationError("The username or password was not correct.")
        self._access_token = response.json()['authentication']['token']


class Token(Authentication):
    def __init__(self, token):
        super(Token, self).__init__()
        self._access_token = token