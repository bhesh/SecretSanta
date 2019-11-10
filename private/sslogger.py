#!/usr/bin/python3
#
# Simple logger
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import logging

LOGGER = logging.getLogger('secretsanta')
LOGGER.setLevel(logging.DEBUG)
fh = logging.FileHander(LOG_FILE)
fh.setLevel(logging.DEBUG)
LOGGER.addHandler(fh)

