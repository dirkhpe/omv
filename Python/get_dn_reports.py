"""
This script will get the denormalized reports. The reports with and without document will be generated.
The script will translate procedure fase into Eerste or Laatste aanleg.
"""

import logging
import os
from lib import my_env
from lib import neostore


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    ns = neostore.NeoStore(cfg)
    dnt = ns.denorm_table_3()
    fn = os.path.join(cfg['Main']['reportdir'], "dn3.csv")
    with open(fn, 'w') as fh:
        logging.info("Trying to write to file {f}".format(f=fn))
        fh.write("aanleg;procedure;procedurestap\n")
        for row in dnt.iterrows():
            aanleg = my_env.aanleg(row[1]['aanleg'])
            procedure = row[1]['procedure']
            stap = row[1]['procedurestap']
            fh.write("{a};{p};{s}\n".format(a=aanleg, p=procedure, s=stap))
