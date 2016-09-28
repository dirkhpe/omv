"""
This script will convert Protege data (in sqlite database) and load it in Neo4J database.
"""

import logging
from lib import datastore
from lib import my_env
from lib import neostore


if __name__ == "__main__":
    # Initialize Environment
    key_list = ["naam", "protege_id", "commentaar", "in_bereik", "afdeling", "artikel", "bladzijde", "hoofdstuk",
                "onderafdeling", "titel", "titel_item", "url"]
    source = 'Protege'
    cfg = my_env.init_env("convert_protege", __file__)
    # Get NeoStore object
    ns = neostore.NeoStore(cfg)
    ns.remove_prot()
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
        component = ns.create_node(source, node_label, **valuedict)
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
        ns.create_relation(node_obj[row["source"]], row["rel_type"], node_obj[row["target"]])
        rel_info.info_loop()
    rel_info.end_loop()
    logging.info('End Application')
