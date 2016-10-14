"""
This script will get the denormalized reports. The reports with and without document will be generated.
"""

import os
from lib import my_env
from lib import neostore


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    ns = neostore.NeoStore(cfg)
    # First get denormalized table for aanleg - procedure - stap
    dnt = ns.denorm_table_3()
    fn = os.path.join(cfg['Main']['reportdir'], "dn3.csv")
    with open(fn, 'w') as fh:
        fh.write("aanleg;procedure;procedurestap\n")
        for row in dnt.iterrows():
            aanleg = row[1]['aanleg']
            procedure = row[1]['procedure']
            stap = row[1]['procedurestap']
            fh.write("{a};{p};{s}\n".format(a=aanleg, p=procedure, s=stap))
    # Then get denormalized report for aanleg - procedure - stap - document
    dnt = ns.denorm_table_4()
    fn = os.path.join(cfg['Main']['reportdir'], "dn4.csv")
    with open(fn, 'w') as fh:
        fh.write("aanleg;procedure;procedurestap;document\n")
        for row in dnt.iterrows():
            aanleg = row[1]['aanleg']
            procedure = row[1]['procedure']
            stap = row[1]['procedurestap']
            doc = row[1]['document']
            fh.write("{a};{p};{s};{d}\n".format(a=aanleg, p=procedure, s=stap, d=doc))
