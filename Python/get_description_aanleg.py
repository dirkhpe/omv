"""
This script will get the description for a dossiertype. It will take Aanleg into account while avoiding the
cartesian product.
It works together with get_graph_aanleg, where the graph will be created.
"""

import argparse
import logging
import os
from lib import neostore
from lib import my_env


if __name__ == "__main__":
    # Configure Command line arguments
    parser = argparse.ArgumentParser(
            description="Script to create a Confluence description for a Dossiertype in 'Omgevingsvergunning' Archief"
    )
    parser.add_argument('-t', '--type', default='Aanvraag Omgevingsvergunning',
                        help='Set the Dossiertype (exact naam!) to start with. Default is "Aanvraag Vergunning".')
    args = parser.parse_args()
    items = []
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    outfile = os.path.join(cfg['Main']['reportdir'], "{n}.txt".format(n=args.type))
    ns = neostore.NeoStore(cfg)
    dosstype_name = args.type
    # Get Node for DossierType
    attribs = {
        "naam": dosstype_name
    }
    dosstype_node = ns.get_node('Dossiertype', 'naam', dosstype_name)
    with open(outfile, 'w') as fh:
        intro = ""
        # fh.write("h1. {n}\n".format(n=dosstype_node["naam"]))
        if dosstype_node["commentaar"]:
            intro += "{{color:purple}}Noot:{{color}} {c}\n".format(c=dosstype_node["commentaar"])
        if ns.get_reference(dosstype_node["protege_id"]):
            intro += "{}".format(ns.get_reference(dosstype_node["protege_id"]))
        if len(intro) > 5:
            fh.write("h1. Introductie\n{}".format(intro))
        dosstype_id = dosstype_node["protege_id"]
        # Get Aanleg for Dossiertype
        aanleg_nodes = ns.get_aanleg4type(dosstype_id)
        for aanleg_node in aanleg_nodes:
            fh.write("h1. {n}\n".format(n=aanleg_node['naam']))
            # Get ProcedureStap for Aanleg
            stap_nodes = ns.get_stap(dosstype_id, aanleg_node['naam'])
            for stap in stap_nodes:
                fh.write("h2. {n}\n".format(n=stap["naam"]))
                if stap["commentaar"]:
                    fh.write("{{color:purple}}Noot:{{color}} {c}\n".format(c=stap["commentaar"]))
                if ns.get_reference(stap["protege_id"]):
                    fh.write("{}".format(ns.get_reference(stap["protege_id"])))
                # Get documenten for Procedure Stap
                doc_array = ns.get_start_nodes(stap, 'bij_procedurestap')
                for doc in doc_array:
                    fh.write("{{color:blue}}{n}{{color}}\n".format(n=doc.start_node()["naam"]))
                    if doc.start_node()["commentaar"]:
                        fh.write("{{color:purple}}Noot:{{color}} {c}\n".format(c=doc.start_node()["commentaar"]))
                    if ns.get_reference(doc.start_node()["protege_id"]):
                        fh.write("{}".format(ns.get_reference(doc.start_node()["protege_id"])))
    logging.info('End Application')
