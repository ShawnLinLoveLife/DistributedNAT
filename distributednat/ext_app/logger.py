#################################################################################
#
# Copyright(C) 2014 Baidu.com, Inc.All right reserved
#
################################################################################
"""
Logger

Brief: This is a logging handler

Author: Zhao Gang <zhaogang05@baidu.com>

Date: 2015-10-30

"""


import os
import logging
import logging.handlers


__all__ = ['get_logger']
TOP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
LOGGER = None


def get_logger():
    """ return the global logger """
    global LOGGER

    if LOGGER is None:
        LOGGER = logging.getLogger("ODL-DISNAT")
        LOGGER.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(name)-12s %(asctime)s %(levelname)-8s %(message)s',
            '%a, %d %b %Y %H:%M:%S',
        )
        log_path = os.path.join(TOP_DIR, 'log')
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_path, "extapp_log"),
            maxBytes=50000000,
            backupCount=3)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        LOGGER.addHandler(file_handler)
        file_handler = logging.FileHandler(os.path.join(log_path, "extapp_err_log"))
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.ERROR)
        LOGGER.addHandler(file_handler)
        file_handler = logging.FileHandler(os.path.join(log_path, "extapp_critical_log"))
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.CRITICAL)
        LOGGER.addHandler(file_handler)

    return LOGGER

