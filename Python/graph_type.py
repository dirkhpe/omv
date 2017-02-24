"""
This script will get the explorer-like graph for a type. It will get the type and calculate the path down.
"""

import argparse
import logging
import os
from graphviz import Digraph
from lib import sqlitestore
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


def go_down(item, branch, level):
    """
    This function will collect all items for which this item is higher in hierarchy.
    So item is target, find all sources.
    @param item:
    @param branch: Remembers the branch of the tree. This allows to handle items more than once, depending on the start
    point.
    @param level: Shows how deep (how many levels) are required
    @return:
    """
    item_list = ds.go_down(item)
    level += 1
    for attribs in item_list:
        item_label = "{br}.{s}".format(br=branch, s=attribs["source"])
        eapp = get_edge_app(attribs["rel_type"])
        dot.edge(item_label, branch, label=attribs["rel_type"], **eapp)
        if item_label not in items:
            # New item, add node and relation, explore item
            items.append(item_label)
            napp = get_node_app(attribs["class"])
            dot.node(item_label, attribs["naam"], **napp)
            if level < args.depth:
                go_down(attribs["source"], item_label, level)


if __name__ == "__main__":
    # Configure Command line arguments
    parser = argparse.ArgumentParser(
            description="Script to create a explorer-like graph for components in 'Omgevingsvergunning' Archief"
    )
    parser.add_argument('-t', '--type', default='Dossiertype',
                        help='Set the component type to start with. Default is "Dossiertype".',
                        choices=['Dossiertype', 'Procedure', 'ProcedureStap', 'Document'])
    parser.add_argument('-d', '--depth', type=int, default=2,
                        help="Set the depth of the graph (default=2). Note that values above 3 don't result "
                             "in readable graphs.")
    args = parser.parse_args()
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    # items is the list of components that have been handled.
    items = []
    ds = sqlitestore.DataStore(cfg)
    # Configure Graph
    dot = Digraph(comment="Overzicht van de structuur.")
    # Configure Graph
    dot.graph_attr['rankdir'] = 'RL'
    dot.graph_attr['bgcolor'] = "#ffffff"
    dot.node_attr['style'] = 'rounded'
    # Get Protege IDs for the required types
    component_list = ds.get_components_type(args.type)
    for comp in component_list:
        # Get Node/Component attributes
        comp_rec = ds.get_comp_attribs(comp)
        if comp_rec is None:
            logging.error("No component record found for {c}.".format(c=comp))
        else:
            items.append(comp)
            node_app = get_node_app(comp_rec["class"])
            dot.node(comp, comp_rec["naam"], **node_app)
            go_down(comp, branch=comp, level=1)
    # Now create and show the graph
    fid = "{t}_{d}".format(t=args.type, d=args.depth)
    graphfile = os.path.join(cfg["Main"]["graphdir"], fid)
    dot.render(graphfile, view=True)
    logging.info('End Application')
