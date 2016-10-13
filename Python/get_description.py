"""
This script will get the description for a dossiertype.
It works together with get_graph.
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
    parser.add_argument('-t', '--type', default='Aanvraag Vergunning',
                        help='Set the Dossiertype (exact naam!) to start with. Default is "Aanvraag Vergunning".')
    args = parser.parse_args()
    items = []
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    outfile = os.path.join(cfg['Main']['logdir'], "{n}.txt".format(n=args.type))
    ns = neostore.NeoStore(cfg)
    dosstype_name = args.type
    # Get Node for DossierType
    attribs = {
        "naam": dosstype_name
    }
    dosstype_node = ns.get_node('Dossiertype', 'naam', dosstype_name)
    with open(outfile, 'w') as fh:
        fh.write("h1. {n}\n".format(n=dosstype_node["naam"]))
        if dosstype_node["commentaar"]:
            fh.write("*Commentaar:* {c}\n".format(c=dosstype_node["commentaar"]))
        # Get ProcedureFase for Dossiertype
        fase_array = ns.get_start_nodes(dosstype_node, 'voor_dossiertype')
        for fase in fase_array:
            fh.write("h2. {n}\n".format(n=fase.start_node()["naam"]))
            if fase.start_node()["commentaar"]:
                fh.write("*Commentaar:* {c}\n".format(c=fase.start_node()["commentaar"]))
            # Get ProcedureStap for ProcedureFase
            stap_array = ns.get_start_nodes(fase.start_node(), 'in_procedure')
            for stap in stap_array:
                fh.write("h3. {n}\n".format(n=stap.start_node()["naam"]))
                if stap.start_node()["commentaar"]:
                    fh.write("*Commentaar:* {c}\n".format(c=stap.start_node()["commentaar"]))
                # Get documenten for Procedure Stap
                doc_array = ns.get_start_nodes(stap.start_node(), 'bij_procedurestap')
                for doc in doc_array:
                    fh.write("{{color:blue}}{n}{{color}}\n".format(n=doc.start_node()["naam"]))
                    if doc.start_node()["commentaar"]:
                        fh.write("{{color:blue}}Commentaar:{{color}} {c}\n".format(c=doc.start_node()["commentaar"]))
    logging.info('End Application')
