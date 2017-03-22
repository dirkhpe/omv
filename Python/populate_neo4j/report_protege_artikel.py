"""
This script will get the denormalized reports. The reports with and without document will be generated.
This script will also add the 'WetArtikels' to the report.
"""

import os
from lib import my_env
from lib import neostore


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    ns = neostore.NeoStore(cfg)
    # First get denormalized table for aanleg - procedure - stap
    dnt = ns.denorm_table_3()
    fn = os.path.join(cfg['Main']['reportdir'], "neo4j_dn3.csv")
    with open(fn, 'w') as fh:
        dossier_item_list, decreet, besluit = ns.denorm_table_3_artikel()
        fh.write("dossiertype;fase;procedurestap;decreet;besluit\n")
        for dossier_item in dossier_item_list.keys():
            try:
                decreet_list = my_env.format_artikels(decreet[dossier_item])
            except KeyError:
                decreet_list = ""
            try:
                besluit_list = my_env.format_artikels(besluit[dossier_item])
            except KeyError:
                besluit_list = ""
            fh.write("{di};{decreet};{besluit}\n".format(di=dossier_item, decreet=decreet_list, besluit=besluit_list))
    # Then get denormalized report for aanleg - procedure - stap - document
    dnt = ns.denorm_table_4()
    fn = os.path.join(cfg['Main']['reportdir'], "neo4j_dn4.csv")
    with open(fn, 'w') as fh:
        dossier_item_list, decreet, besluit = ns.denorm_table_4_artikel()
        fh.write("dossiertype;fase;procedurestap;document;decreet;besluit\n")
        for dossier_item in dossier_item_list.keys():
            try:
                decreet_list = my_env.format_artikels(decreet[dossier_item])
            except KeyError:
                decreet_list = ""
            try:
                besluit_list = my_env.format_artikels(besluit[dossier_item])
            except KeyError:
                besluit_list = ""
            fh.write("{di};{decreet};{besluit}\n".format(di=dossier_item, decreet=decreet_list, besluit=besluit_list))
