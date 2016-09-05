"""
This script will convert Protege data (in sqlite database) and load it in Neo4J database.
"""

import sys
import logging
from lib import datastore
from lib import my_env
from py2neo import Graph, Node, Relationship


# Initialize Environment
key_list = ["naam", "protege_id", "beschrijving", "formaat", "in_bereik"]
cfg = my_env.init_env("convert_protege", __file__)
# Get Neo4J Connetion and clean Database
graph = Graph()
query = "MATCH (n) DETACH DELETE n"
try:
    graph.cypher.execute(query)
except:
    e = sys.exc_info()[1]
    ec = sys.exc_info()[0]
    log_msg = "Neo4J not running? Error Class: %s, Message: %s"
    logging.critical(log_msg, ec, e)
    sys.exit(1)
# Database clean
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
    graph.create_unique(rel)
    rel_info.info_loop()
rel_info.end_loop()
logging.info('End Application')
