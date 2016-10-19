"""
This script will get the graph starting from an object. Relations are in bottom-up direction. There will be an walk-up
and walk-down.
"""

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
    if rel_type == "voor_dossiertype":
        edge_appearance = {'color': "#DC3800"}
    elif rel_type == "in_procedure":
        edge_appearance = {'color': "#75B095"}
    elif rel_type == "bij_procedurestap":
        edge_appearance = {'color': "#DC3800"}
    else:
        logger.error("Relation Type {rt} not defined.".format(rt=rel_type))
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
    elif node_class == "ProcedureFase":
        node_appearance = {'fillcolor': "#EAD800",
                           'shape': "box",
                           'style': "filled"}
    elif node_class == "Dossiertype":
        node_appearance = {'fillcolor': "#DC3800",
                           'shape': "egg",
                           'style': "filled"}
    else:
        logger.error("Node Class {nc} not defined.".format(nc=node_class))
        node_appearance = {'fillcolor': "#DC3800",
                           'shape': "egg",
                           'style': "filled"}
    return node_appearance


if __name__ == "__main__":
    items = []
    cfg = my_env.init_env("convert_protege", __file__)
    logger = logging.getLogger(cfg['Main']['logname'])
    ns = neostore.NeoStore(cfg)
    # Configure Graph
    dot = Digraph(comment="Overzicht")
    dot.graph_attr['rankdir'] = 'RL'
    dot.graph_attr['bgcolor'] = "#ffffff"
    dot.node_attr['style'] = 'rounded'
#    dt_nodes = ["archief_structuur_Class150095", "archief_structuur_Class21", "archief_structuur_Class30",
#                "archief_structuur_Class32", "archief_structuur_Class28", "archief_structuur_Class29"]
    dt_node_inp = cfg["DossierGroup"]["Group"]
    dt_nodes = dt_node_inp.split()
    rel_df = ns.get_relations_togroup("ProcedureFase", "Dossiertype", "voor_dossiertype", dt_nodes)
    to_nodes = []
    for rel in rel_df.iterrows():
        # Is this a known Dossiertype?
        dt_id = rel[1]["t_id"]
        dt_naam = rel[1]["t_naam"]
        if dt_id not in items:
            # Create Node
            node_app = get_node_app("Dossiertype")
            dot.node(dt_id, dt_naam, **node_app)
            items.append(dt_id)
        # Is this a known ProcedureFase?
        pf_id = rel[1]["f_id"]
        pf_naam = rel[1]["f_naam"]
        if pf_id not in items:
            # Create Node
            node_app = get_node_app("ProcedureFase")
            dot.node(pf_id, pf_naam, **node_app)
            items.append(pf_id)
            to_nodes.append(pf_id)
        # Set relation between procedurefase and dossiertype
        dot.edge(pf_id, dt_id)
    rel_df = ns.get_relations_togroup("ProcedureStap", "ProcedureFase", "in_procedure", to_nodes)
    for rel in rel_df.iterrows():
        # Is this a known ProcedureFase?
        pf_id = rel[1]["t_id"]
        pf_naam = rel[1]["t_naam"]
        if pf_id not in items:
            # Create Node
            node_app = get_node_app("ProcedureFase")
            dot.node(pf_id, pf_naam, **node_app)
            items.append(pf_id)
        # Is this a known ProcedureStap?
        dt_id = rel[1]["f_id"]
        dt_naam = rel[1]["f_naam"]
        if dt_id not in items:
            # Create Node
            node_app = get_node_app("ProcedureStap")
            dot.node(dt_id, dt_naam, **node_app)
            items.append(dt_id)
        # Set relation between procedurefase and dossiertype
        dot.edge(dt_id, pf_id)
    graphfile = os.path.join(cfg["Main"]["graphdir"], 'overview')
    dot.render(graphfile, view=True)
    dot.save("overview.dot", cfg["Main"]["graphdir"])

    logger.info('End Application')
