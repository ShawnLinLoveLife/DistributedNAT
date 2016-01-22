#################################################################################
#
# Copyright(C) 2014 Baidu.com, Inc.All right reserved
#
################################################################################
"""
Config

Brief: This is a parser of configuration file

Author: Zhao Gang <zhaogang05@baidu.com>

Date: 2015-10-30

"""


import os
import ConfigParser


__all__ = ['get_config']
TOP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CONF = None


def get_config():
    """ return the global config parser """
    #Read the config file and initialize the return code
    global CONF

    if CONF is None:
        CONF = ConfigParser.ConfigParser()
        CONF.read(os.path.join(TOP_DIR, "conf/ext_app.cfg"))
    return CONF
