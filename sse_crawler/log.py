# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 11:15:27 2020

@author: 19424
"""


import logging


def get_my_logger(log_paths=None):
    """
    Get a logger, with INFO level streamhandler by default.
    Add your own handlers by defining a list of log paths.

    Keyword arguments:
    log_paths -- a list of (filename, logging.severity) couples (Default None)
    """
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatterc = logging.Formatter('%(message)s')
    ch.setFormatter(formatterc)
    logger.addHandler(ch)

    if log_paths:
        formatterf = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        def add_filehandler(log_path):
            fh = logging.FileHandler(log_path[0])
            fh.setLevel(log_path[1])
            fh.setFormatter(formatterf)
            logger.addHandler(fh)
        
        for log_path in log_paths:
            add_filehandler(log_path)
            
    return logger