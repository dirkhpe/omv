"""
This script will consolidate the information from all sources in the vo_omv_ar database.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
from lib import my_env
from lib.my_env import run_script
from lib import mysqlstore


if __name__ == "__main__":

    cfg = my_env.init_env('convert_protege', __file__)

    # Set up environment
    (fp, _) = os.path.split(__file__)

    # Drop and recreate database vo_omv_ar
    db = cfg['ConsolidationDB']['db']
    user = cfg['ConsolidationDB']['user']
    pwd = cfg['ConsolidationDB']['pwd']
    logging.info("Drop and recreate database {db}.".format(db=db))
    mysqlstore.DirectConn(db=db, user=user, pwd=pwd)

    tocs = ['Uitvoeringsbesluit', 'Decreet']
    for toc in tocs:
        logging.info('Import Table of Content for {toc}'.format(toc=toc))
        run_script(fp, 'import_toc.py', '-s', toc)

    logging.info('Get artefacts from Protege')
    run_script(fp, 'collect_protege.py')

    logging.info('Reconfigure Openbaar Onderzoek voor type Voorwerp Duur')
    run_script(fp, 'voorwerpduur_oo.py')

    logging.info('Link artefacts to Artikels')
    run_script(fp, 'collect_protege_artikels.py')

    logging.info('Get information from Uitwisselingsplatform (postgres)')
    run_script(fp, 'collect_postgres.py')

    logging.info('Map information Uitwisselingsplatform and Archief')
    run_script(fp, 'map_up_ar.py')
