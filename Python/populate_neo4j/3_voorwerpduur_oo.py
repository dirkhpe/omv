"""
This script will handle duplicate 'Openbaar Onderzoek' during 'Eerste Aanleg'.
This will be done in steps listed below:
1. Create node 'Openbaar Onderzoek bij bekendmaking inspraakprocedure'
2. Get all Documenten from 'Openbaar Onderzoek', link them with new node 'Openbaar Onderzoek bij bekendmaking
    inspraakprocedure'
3. Link new node with 'VoorwerpDuur * Samenstellen Eerste Aanleg'
4. Remove link 'Openbaar Onderzoek' naar 'VoorwerpDuur * Samenstellen Eerste Aanleg'
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
import uuid
from lib import my_env
from lib import neostore


if __name__ == '__main__':
    cfg = my_env.init_env("convert_protege", __file__)
    # Get NeoStore object
    ns = neostore.NeoStore(cfg)
    # Create node "Openbaar Onderzoek bij bekendmaking inspraakprocedure"
    attribs = {
        'protege_id': str(uuid.uuid4()),
        'naam': 'Openbaar Onderzoek bij Bekendmaking',
        'label': 'Openbaar Onderzoek bij Bekendmaking',
        'in_bereik': 'true',
        'commentaar': 'Er is dubbel Openbaar Onderzoek in Eerste Aanleg bij Bijstelling Voorwerp Duur '
                      'Omgevingsvergunning'
    }
    new_oo_node = ns.create_node('ProcedureStap', 'Protege', **attribs)
    # Get all documents linked with Openbaar Onderzoek, link them with new node
    current_oo_node = ns.get_node('ProcedureStap', 'naam', 'Openbaar Onderzoek')
    doc_rels = ns.get_start_nodes(end_node=current_oo_node, rel_type="bij_procedurestap")
    for doc_rel in doc_rels:
        doc_node = doc_rel.start_node()
        logging.info("Link {doc} with {oo}".format(doc=doc_node["naam"], oo=new_oo_node["naam"]))
        ns.create_relation(left_node=doc_node, rel="bij_procedurestap", right_node=new_oo_node)
    # Find link Openbaar Onderzoek naar Samenstellen Eerste Aanleg
    attribs = {
        'naam': "Bijstelling voorwerp of duur van omgevingsvergunning"
    }
    pf_node = ns.get_node('ProcedureFase', 'label', 'VoorwerpDuur * Samenstellen Eerste Aanleg')
    ns.del_relation(from_node=current_oo_node, rel_type="in_procedure", to_node=pf_node)
    ns.create_relation(left_node=new_oo_node, rel="in_procedure", right_node=pf_node)
