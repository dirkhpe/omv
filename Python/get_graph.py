"""
This script will get the graph starting from an object. Relations are in bottom-up direction. There will be an walk-up
and walk-down.
"""

import logging
from graphviz import Digraph
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
    for attribs in item_list:
        dot.edge(attribs["source"], item, label=attribs["rel_type"])
        if attribs["source"] not in items:
            # New item, add node and relation, explore item
            items.append(attribs["source"])
            dot.node(attribs["source"], attribs["naam"])
            go_down(attribs["source"])


def go_up(item):
    """
    This function will collect all items for which this item is lower in hierarchy.
    So item is source, find all targets.
    @param item:
    @return:
    """
    item_list = ds.go_up(item)
    for attribs in item_list:
        dot.edge(item, attribs["target"], label=attribs["rel_type"])
        if attribs["target"] not in items:
            # New item, add node and relation, explore item
            items.append(attribs["target"])
            dot.node(attribs["target"], attribs["naam"])
            go_up(attribs["target"])


if __name__ == "__main__":
    items = []
    cfg = my_env.init_env("convert_protege", __file__)
    ds = datastore.DataStore(cfg)
    center = "struct_Class30035"
    # Get Node attributes
    center_rec = ds.get_comp_attribs(center)
    if center_rec is None:
        logging.error("No component record found for {c}.".format(c=center))
    else:
        items.append(center)
        dot = Digraph(comment="Overzicht voor {n}".format(n=center_rec["naam"]))
        dot.graph_attr['rankdir'] = 'RL'
        dot.node(center, center_rec["naam"])
        go_up(center)
        go_down(center)
        dot.render("c:/temp/test.gv", view=True)
    logging.info('End Application')
