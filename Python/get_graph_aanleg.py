"""
Rework of get_graph.py to keep track of aanleg instead of ProcedureFase. Use Neo4J instead of SQLite as datastore.
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
    if rel_type == "aanleg":
        edge_appearance = {'color': "#DC3800"}
    elif rel_type == "stap":
        edge_appearance = {'color': "#75B095"}
    elif rel_type == "document":
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
    elif node_class == "Aanleg":
        node_appearance = {'fillcolor': "#EAD800",
                           'shape': "box",
                           'style': "filled"}
    elif node_class == "Dossiertype":
        node_appearance = {'fillcolor': "#00FFFF",
                           'shape': "egg",
                           'style': "filled"}
    else:
        logging.error("Node Class {nc} not defined.".format(nc=node_class))
        node_appearance = {'fillcolor': "#DC3800",
                           'shape': "egg",
                           'style': "filled"}
    return node_appearance


if __name__ == "__main__":
    # Configure Command line arguments
    parser = argparse.ArgumentParser(
            description="Script to create a Confluence Graph for a Dossiertype in 'Omgevingsvergunning' Archief"
    )
    parser.add_argument('-t', '--type', default='Aanvraag Omgevingsvergunning',
                        help='Set the Dossiertype (exact naam!) to start with. '
                             'Default is "Aanvraag Omgevingsvergunning".')
    args = parser.parse_args()
    items = []
    relations = []
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    outfile = os.path.join(cfg['Main']['reportdir'], "{n}.txt".format(n=args.type))
    ns = neostore.NeoStore(cfg)
    dosstype_name = args.type
    # Configure Graph
    dot = Digraph(comment="Overzicht voor {n}".format(n=dosstype_name))
    dot.graph_attr['rankdir'] = 'LR'
    dot.graph_attr['bgcolor'] = "#ffffff"
    dot.node_attr['style'] = 'rounded'
    # Get Node for DossierType to get protege_id for further processing
    attribs = {
        "naam": dosstype_name
    }
    dosstype_node = ns.get_node('Dossiertype', 'naam', dosstype_name)
    dosstype_id = dosstype_node["protege_id"]
    items.append(dosstype_id)
    # Add Node to the graph
    node_app = get_node_app('Dossiertype')
    dot.node(dosstype_id, dosstype_name, **node_app)
    # Get Aanleg for Dossiertype
    aanleg_nodes = ns.get_aanleg4type(dosstype_id)
    for aanleg_node in aanleg_nodes:
        # Add Node to the graph
        if aanleg_node["naam"] not in items:
            items.append(aanleg_node["naam"])
            node_app = get_node_app('Aanleg')
            dot.node(aanleg_node['naam'], aanleg_node['naam'], **node_app)
        # Add Relation from Dossiertype to Aanleg
        rel_name = "{f}->{t}".format(f=dosstype_id, t=aanleg_node["naam"])
        if rel_name not in relations:
            relations.append(rel_name)
            eapp = get_edge_app('aanleg')
            dot.edge(dosstype_id, aanleg_node['naam'], label='aanleg', **eapp)
        # Get ProcedureStap for Aanleg
        stap_nodes = ns.get_stap(dosstype_id, aanleg_node['naam'])
        for stap in stap_nodes:
            # Add Node to the graph
            if stap["protege_id"] not in items:
                items.append(stap["protege_id"])
                node_app = get_node_app('ProcedureStap')
                dot.node(stap['protege_id'], stap['naam'], **node_app)
            # Add Relation from Dossiertype to Aanleg
            rel_name = "{f}->{t}".format(f=aanleg_node["naam"], t=stap['protege_id'])
            if rel_name not in relations:
                relations.append(rel_name)
                eapp = get_edge_app('stap')
                dot.edge(aanleg_node['naam'], stap['protege_id'], label='stap', **eapp)
            # Get documenten for Procedure Stap
            doc_array = ns.get_start_nodes(stap, 'bij_procedurestap')
            for doc in doc_array:
                # Add Node to the graph
                if doc.start_node()["protege_id"] not in items:
                    items.append(doc.start_node()["protege_id"])
                    node_app = get_node_app('Document')
                    dot.node(doc.start_node()["protege_id"], doc.start_node()["naam"], **node_app)
                # Add Relation from Dossiertype to Aanleg
                rel_name = "{f}->{t}".format(f=stap['protege_id'], t=doc.start_node()["protege_id"])
                if rel_name not in relations:
                    relations.append(rel_name)
                    eapp = get_edge_app('document')
                    dot.edge(stap['protege_id'], doc.start_node()["protege_id"], label='document', **eapp)
    graphfile = os.path.join(cfg["Main"]["graphdir"], dosstype_name)
    dot.render(graphfile, view=True)
    dot.save("{}.dot".format(dosstype_name), cfg["Main"]["graphdir"])
    logging.info('End Application')
