"""
This script will convert Protege data (in sqlite database) and load it in Neo4J database.
"""

import logging
from lib import sqlitestore
from lib import my_env
from lib import neostore


if __name__ == "__main__":
    # Initialize Environment
    key_list = ["naam", "protege_id", "commentaar", "in_bereik", "afdeling", "artikel", "bladzijde", "hoofdstuk",
                "onderafdeling", "titel", "titel_item", "url", "label"]
    source = 'Protege'
    cfg = my_env.init_env("convert_protege", __file__)
    # Get NeoStore object
    ns = neostore.NeoStore(cfg)
    # Clean Neo4J for node labels that will be restored
    labels = ['Protege', 'Artikel', 'Aanleg']
    for label in labels:
        logging.info('Remove nodes with label {l}'.format(l=label))
        ns.remove_nodes(label)
    # Get DataStore object
    ds = sqlitestore.DataStore(cfg)
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

    # First get all book toc nodes
    toc = {}
    dn = ns.get_nodes('Decreet')
    for node in dn:
        toc[node["toc"]] = node
    un = ns.get_nodes('Uitvoeringsbesluit')
    for node in un:
        toc[node["toc"]] = node
    # Also get book nodes
    book_nodes = {}
    bn = ns.get_nodes('Boek')
    for node in bn:
        book_nodes[node["item"]] = node
    # Initialize Artikel Nodes dictionary
    art_nodes = {}
    # Initialize Artikel in TOC nodes
    art_in_toc = {}

    # Handle relations
    rel2handle = ["voor_dossiertype", "in_procedure", "bij_procedurestap"]
    rel2book = ["beschreven_in"]
    rows = ds.get_relations()
    rel_info = my_env.LoopInfo("Relations", 10)
    for row in rows:
        if row["rel_type"] in rel2handle:
            ns.create_relation(node_obj[row["source"]], row["rel_type"], node_obj[row["target"]])
        elif row["rel_type"] in rel2book:
            this_toc = ds.toc4item(row["target"])
            try:
                ns.create_relation(node_obj[row["source"]], row["rel_type"], toc[this_toc])
            except KeyError:
                logging.error("Try to relate proc {p} to item {i}, but toc {t} not found".format(p=row["source"],
                                                                                                 i=row["target"],
                                                                                                 t=this_toc))
            # Check if we have Artikel nummer. If so, handle artikel nummer
            if ds.art4item(row["target"]):
                art, book = ds.art4item(row["target"])
                art_id = "{b}_{a}".format(a=art, b=book)
                try:
                    art_node = art_nodes[art_id]
                except KeyError:
                    # Create artikel-book node
                    node_label = "Artikel"
                    valuedict = {
                        'artikel': art
                    }
                    art_node = ns.create_node(node_label, **valuedict)
                    art_nodes[art_id] = art_node
                    # Link artikel to boek
                    ns.create_relation(art_node, 'artikel_in_boek', book_nodes[book])
                # Artikel Node - Boek relation exist, now add relation Artikel to Item
                ns.create_relation(node_obj[row["source"]], 'in_artikel', art_node)
                # Also check for Artikel to TOC link. create_relation will add the artikel to TOC only once.
                ns.create_relation(art_node, 'artikel_in_toc', toc[this_toc])
        rel_info.info_loop()
    rel_info.end_loop()
    logging.info('End Application')
