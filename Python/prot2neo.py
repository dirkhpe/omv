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
    ns.remove_nodes('Protege')
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

    # First get all book nodes
    toc = {}
    dn = ns.get_nodes('Decreet')
    for node in dn:
        toc[node["toc"]] = node
    un = ns.get_nodes('Uitvoeringsbesluit')
    for node in un:
        toc[node["toc"]] = node

    # Handle relations
    rel2handle = ["voor_dossiertype", "in_procedure", "bij_procedurestap"]
    rel2book = ["beschreven_in"]
    rows = ds.get_relations()
    rel_info = my_env.LoopInfo("Relations", 10)
    for row in rows:
        if row["rel_type"] in rel2handle:
            ns.create_relation(node_obj[row["source"]], row["rel_type"], node_obj[row["target"]])
        elif row["rel_type"] in rel2book:
            # this_toc = ds.toc4item(row["target"])
            ns.create_relation(node_obj[row["source"]], row["rel_type"], toc["3.10.1.1."])
        rel_info.info_loop()
    rel_info.end_loop()
    logging.info('End Application')
