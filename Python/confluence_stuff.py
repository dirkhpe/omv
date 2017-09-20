"""
This script will produce all output required for confluence. It will call get_dn_reports to get the denormalized
reports. It will also get all Dossiertypes and call get_description and get_graph for each Dossiertype.
"""

import logging
import os
import subprocess
import sys
from lib import my_env
from lib import neostore

if __name__ == "__main__":
    cfg = my_env.init_env('convert_protege', __file__)
    # logger = logging.getLogger(cfg['Main']['logname'])
    (filepath, filename) = os.path.split(__file__)
    python_path = sys.executable
    script = os.path.join(filepath, 'report_protege.py')
    logging.info("Run Denormalized Reports script")
    res = subprocess.call([python_path, script], env=os.environ.copy())
    ns = neostore.NeoStore(cfg)
    dt = ns.get_nodes('Dossiertype')
    script_desc = os.path.join(filepath, 'get_description.py')
    script_graph = os.path.join(filepath, 'get_graph.py')
    for dn in dt:
        naam = dn["naam"]
        logging.info("Get description file for {}".format(naam))
        subprocess.call([python_path, script_desc, '-t', naam])
        p_id = dn["protege_id"]
        logging.info("Get graph for {}".format(p_id))
        subprocess.call([python_path, script_graph, p_id])
