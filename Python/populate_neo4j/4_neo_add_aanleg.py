"""
This script will add Nodes of type 'Aanleg' by consolidating nodes of type 'ProcedureFase'.
However this is not a good procedure. It will add all possible dossiertype - aanleg links and all possible
aanleg - procedurestap links. This combines to cartesian product dossiertype - aanleg - procedurestap, and this is not
necessary required.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
from lib import my_env
from lib import neostore


if __name__ == '__main__':
    cfg = my_env.init_env("convert_protege", __file__)
    # Get NeoStore object
    ns = neostore.NeoStore(cfg)
    ns.remove_nodes('Aanleg')
    aanleg_arr = ['Eerste Aanleg', 'Laatste Aanleg']
    for aanleg in aanleg_arr:
        # Create Node aanleg
        logging.info("Create Aanleg Node {n}".format(n=aanleg))
        props = {
            'naam': aanleg,
            'label': aanleg
        }
        aanleg_node = ns.create_node('Aanleg', **props)
        cursor = ns.get_aanleg_paths(aanleg)
        while cursor.forward():
            record = cursor.current()
            (dtn, pfn, psn) = record.values()
            # Create relations
            ns.create_relation(left_node=aanleg_node, rel='aanleg_bij_type', right_node=dtn)
            ns.create_relation(left_node=psn, rel='in_aanleg', right_node=aanleg_node)
            ns.create_relation(left_node=pfn, rel='aanleg', right_node=aanleg_node)
    # Then handle all paths where aanleg node not 'Eerste Aanleg' or 'Laatste Aanleg'
    aanleg_nodes = {}
    cursor = ns.get_no_aanleg_paths()
    while cursor.forward():
        record = cursor.current()
        (dtn, pfn, psn) = record.values()
        # Get the aanleg node
        try:
            aanleg_node = aanleg_nodes[pfn['naam']]
        except KeyError:
            # Create the aanleg Node
            logging.info("Create Aanleg Node {n}".format(n=pfn['naam']))
            props = {
                'naam': pfn['naam'],
                'label': pfn['naam']
            }
            aanleg_node = ns.create_node('Aanleg', **props)
            # Remember aanleg_node!
            aanleg_nodes[pfn['naam']] = aanleg_node
        # Create relations
        ns.create_relation(left_node=aanleg_node, rel='aanleg_bij_type', right_node=dtn)
        ns.create_relation(left_node=psn, rel='in_aanleg', right_node=aanleg_node)
        ns.create_relation(left_node=pfn, rel='aanleg', right_node=aanleg_node)
