"""
This script will get the explorer-like graph for a book. It will get the book label and calculate the path down.
"""

import argparse
import logging
import os
from graphviz import Digraph
from lib import neostore
from lib import my_env


def get_edge_app(rel_type):
    """
    This procedure will create the dictionary that defines the edge appearance for this type of relations.
    @param rel_type: Type of the relation
    @return: dictionary to define appearance of the edge.
    """
    if rel_type == "in_procedure":
        edge_appearance = {'color': "#DC3800"}
    elif rel_type == "in_procedurestap":
        edge_appearance = {'color': "#75B095"}
    elif rel_type == "bij_procedurestap":
        edge_appearance = {'color': "#75B095"}
    elif rel_type == "voor_dossiertype":
        edge_appearance = {'color': "#DC3800"}
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
        node_appearance = {'fillcolor': "#B3801C",
                           'shape': "box",
                           'style': "filled"}
    else:
        logging.error("Node Class {nc} not defined.".format(nc=node_class))
        node_appearance = {'fillcolor': "#DC3800",
                           'shape': "egg",
                           'style': "filled"}
    return node_appearance


def add_node(nid, nlabel):
    napp = get_node_app('Document')
    dot.node(nid, label=nlabel, **napp)
    items.append(nid)
    return


def handle_comps(comp_list):
    """
    This function will handle all nodes and relations in comp_list.
    @param comp_list:
    @return:
    """
    for cr in comp_list.iterrows():
        llabel = cr[1]['llabel']
        rlabel = cr[1]['rlabel']
        lid = "dot_{}".format(cr[1]['lid'])
        rid = "dot_{}".format(cr[1]['rid'])
        if lid not in items:
            add_node(lid, llabel)
        if rid not in items:
            add_node(rid, rlabel)
        eapp = get_edge_app('in_procedure')
        dot.edge(lid, rid, label='heeft deel', **eapp)


if __name__ == "__main__":
    # Configure Command line arguments
    parser = argparse.ArgumentParser(
            description="Script to create a explorer-like graph for book table of contents"
    )
    parser.add_argument('-s', '--sheet', default='Decreet 25.04.14',
                        help='Worksheet name. Default is "Decreet 25.04.14".',
                        choices=['Decreet 25.04.14', '(to be completed)'])
    args = parser.parse_args()
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    # items is the list of components that have been handled.
    items = []
    ns = neostore.NeoStore(cfg)
    # Configure Graph
    dot = Digraph(comment="Inhoudstafel voor {b}.".format(b=args.sheet))
    # Configure Graph
    dot.graph_attr['rankdir'] = 'LR'
    dot.graph_attr['bgcolor'] = "#ffffff"
    dot.node_attr['style'] = 'rounded'
    # Get all book - titel nodes and relations for book
    component_list = ns.get_components_book('book', blabel=args.sheet)
    handle_comps(component_list)
    component_list = ns.get_components_book('Titel', blabel=args.sheet)
    handle_comps(component_list)
    component_list = ns.get_components_book('Hoofdstuk', blabel=args.sheet)
    handle_comps(component_list)
    component_list = ns.get_components_book('Afdeling', blabel=args.sheet)
    handle_comps(component_list)
    # Now create and show the graph
    fid = "{t}".format(t=args.sheet)
    graphfile = os.path.join(cfg["Main"]["graphdir"], fid)
    dot.render(graphfile, view=True)
    logging.info('End Application')
