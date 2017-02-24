"""
This script will load Postgres Primary - Foreign Key relations into Neo4J database.
"""

import logging
from lib import sqlitestore
from lib import my_env
from lib import neostore

tables = []
node_obj = {}
source = 'Postgres'


def handle_item(name):
    if name not in tables:
        tables.append(name)
        valuedict = dict(
            name=name
        )
        new_node = ns.create_node(source, **valuedict)
        node_obj[name] = new_node
        return True
    else:
        return False

if __name__ == "__main__":
    # Initialize Environment
    key_list = ["naam", "protege_id", "commentaar", "in_bereik", "afdeling", "artikel", "bladzijde", "hoofdstuk",
                "onderafdeling", "titel", "titel_item", "url", "label"]
    cfg = my_env.init_env("convert_protege", __file__)
    # Get NeoStore object
    ns = neostore.NeoStore(cfg)
    # Clean Neo4J for node labels that will be restored
    labels = [source]
    for label in labels:
        logging.info('Remove nodes with label {l}'.format(l=label))
        ns.remove_nodes(label)
    # Get DataStore object
    ds = sqlitestore.DataStore(cfg)
    # Get all Component rows
    rows = ds.get_pg_tables()
    node_info = my_env.LoopInfo("Nodes", 10)
    for row in rows:
        fk_table = row['FK_Table']
        pk_table = row['PK_Table']
        if handle_item(name=fk_table):
            node_info.info_loop()
        if handle_item(name=pk_table):
            node_info.info_loop()
        # I got a unique list of relations, so no need to check. Relation can be added.
        ns.create_relation(node_obj[fk_table], "fk", node_obj[pk_table])
        node_info.info_loop()
    node_info.end_loop()
    logging.info('End Application')
