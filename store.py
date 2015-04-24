#!/usr/bin/env python
"""Implements a data store for BaseCRM objects"""

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


class Store(object):
    pass


class InMemory(Store):
    def __init__(self):
        self.device_id = None