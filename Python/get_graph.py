"""
This script will get the graph starting from an object. Relations are in bottom-up direction. There will be an walk-up
and walk-down.
"""

import logging
from lib import datastore
from lib import my_env


def go_down(item):
    """
    This function will collect all items for which this item is higher in hierarchy.
    So item is target, find all sources.
    @param item:
    @return:
    """
    item_list = ds.go_down(item)



if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    ds = datastore.DataStore(cfg)
    center = "Structuur_Class30023"
    # go_up(center)
    go_down(center)
    logging.info('End Application')
