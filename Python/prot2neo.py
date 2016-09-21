"""
This script will convert Protege data (in sqlite database) and load it in Neo4J database.
"""

import sys
import logging
from lib import datastore
from lib import my_env
from py2neo import Graph, Node, Relationship


if __name__ == "__main__":
    # Initialize Environment
    key_list = ["naam", "protege_id", "commentaar", "in_bereik"]
    cfg = my_env.init_env("convert_protege", __file__)
    # Get Neo4J Connetion and clean Database
    neo4j_config = {
        'user': cfg['Graph']['username'],
        'password': cfg['Graph']['password'],
    }
    graph = Graph(**neo4j_config)
    logging.info("Connected to Graph, now trying to remove all nodes and relations.")
    try:
        graph.delete_all()
    except:
        logging.exception("Something happened: ")
        sys.exit(1)
    # Get DataStore object
    ds = datastore.DataStore(cfg)
    # Get all Component rows
    rows = ds.get_components()
    node_obj = {}
    node_info = my_env.LoopInfo("Nodes", 10)
    for row in rows:
        node_label = row["class"]
        valuedict = {}
        for attrib in key_list:
            if row[attrib]:
                valuedict[attrib.lower()] = str(row[attrib])
        component = Node(node_label, **valuedict)
        graph.create(component)
        # Remember component for Relation in next step
        node_obj[row["protege_id"]] = component
        node_info.info_loop()
    node_info.end_loop()

    logging.debug("Been there, done that")
    for k in node_obj.keys():
        logging.debug("Key: {k}".format(k=k))

    # Handle relations
    rows = ds.get_relations()
    rel_info = my_env.LoopInfo("Relations", 10)
    for row in rows:
        rel = Relationship(node_obj[row["source"]], row["rel_type"], node_obj[row["target"]])
        graph.merge(rel)
        rel_info.info_loop()
    rel_info.end_loop()
    logging.info('End Application')
