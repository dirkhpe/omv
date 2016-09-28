"""
This script will get the graph starting from an object. Relations are in bottom-up direction. There will be an walk-up
and walk-down.
"""

import logging
import os
import sys
from graphviz import Digraph
from lib import datastore
from lib import my_env


def get_edge_app(rel_type):
    """
    This procedure will create the dictionary that defines the edge appearance for this type of relations.
    @param rel_type: Type of the relation
    @return: dictionary to define appearance of the edge.
    """
    if rel_type == "stuk_in_map":
        edge_appearance = {'color': "#DC3800"}
    elif rel_type == "deelmap_van":
        edge_appearance = {'color': "#75B095"}
    else:
        logging.error("Relation Type {rt} not defined.".format(rt=rel_type))
        edge_appearance = {'color': "#000000"}
    return edge_appearance


def get_node_app(node_class):
    """
    This procedure will create the dictionary that defines the node appearance for this class of nodes.
    @param node_class: Class of the Node
    @return: dictionary to define appearance of the node
    """
    if node_class == "Document":
        node_appearance = {'fillcolor': "#EAD800",
                           'shape': "box",
                           'style': "filled"}
    elif node_class == "ProcedureStap":
        node_appearance = {'fillcolor': "#B3801C",
                           'shape': "box",
                           'style': "filled"}
    elif node_class == "Procedure":
        node_appearance = {'fillcolor': "#EAD800",
                           'shape': "box",
                           'style': "filled"}
    elif node_class == "Dossiertype":
        node_appearance = {'fillcolor': "#DC3800",
                           'shape': "egg",
                           'style': "filled"}
    else:
        logging.error("Node Class {nc} not defined.".format(nc=node_class))
        node_appearance = {'fillcolor': "#DC3800",
                           'shape': "egg",
                           'style': "filled"}
    return node_appearance


def go_down(item):
    """
    This function will collect all items for which this item is higher in hierarchy.
    So item is target, find all sources.
    @param item:
    @return:
    """
    item_list = ds.go_down(item)
    for attribs in item_list:
        eapp = get_edge_app(attribs["rel_type"])
        dot.edge(attribs["source"], item, label=attribs["rel_type"], **eapp)
        if attribs["source"] not in items:
            # New item, add node and relation, explore item
            items.append(attribs["source"])
            napp = get_node_app(attribs["class"])
            dot.node(attribs["source"], attribs["naam"], **napp)
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
        eapp = get_edge_app(attribs["rel_type"])
        dot.edge(item, attribs["target"], label=attribs["rel_type"], **eapp)
        if attribs["target"] not in items:
            # New item, add node and relation, explore item
            items.append(attribs["target"])
            napp = get_node_app(attribs["class"])
            dot.node(attribs["target"], attribs["naam"], **napp)
            go_up(attribs["target"])


if __name__ == "__main__":
    items = []
    cfg = my_env.init_env("convert_protege", __file__)
    ds = datastore.DataStore(cfg)
    # center = "struct_Class30035"
    center = sys.argv[1]
    # Get Node attributes
    center_rec = ds.get_comp_attribs(center)
    if center_rec is None:
        logging.error("No component record found for {c}.".format(c=center))
    else:
        items.append(center)
        dot = Digraph(comment="Overzicht voor {n}".format(n=center_rec["naam"]))
        # Configure Graph
        dot.graph_attr['rankdir'] = 'RL'
        dot.graph_attr['bgcolor'] = "#ffffff"
        dot.node_attr['style'] = 'rounded'
        node_app = get_node_app(center_rec["class"])
        dot.node(center, center_rec["naam"], **node_app)
        go_up(center)
        go_down(center)
        graphfile = os.path.join(cfg["Main"]["graphdir"], center)
        dot.render(graphfile, view=True)
        dot.save("{}.dot".format(center), cfg["Main"]["graphdir"])

    logging.info('End Application')
