"""
This script will report on the data from the 'Regelgeving'.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
from lib import my_env
from lib import mysqlstore as mysql
from lib.mysqlstore import *


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])
    fn = os.path.join(cfg['Main']['reportdir'], "sql_dn3fase.csv")
    fh = open(fn, 'w')
    fh.write("aanleg;FID;procedure;DID;procedurestap;SID\n")
    """
    for dossier in cons_sess.query(ArType).filter(ArType.fases.any()):
        for fase in dossier.fases:
            for fase_stap in cons_sess.query(ArFase).filter(ArFase.stappen.any(id=fase.id)):
                for stap in fase_stap.stappen:
                    fh.write("{f};{fid};{d};{did};{s};{sid}\n".format(d=dossier.naam, f=fase.naam, s=stap.naam,
                                                                      fid=fase.id, did=dossier.id, sid=stap.id))
    """
    for fase_stap in cons_sess.query(ArFase).filter(ArFase.stappen.any()):
        for stap in fase_stap.stappen:
            fh.write("{f};{fid};{d};{did};{s};{sid}\n".format(d=None, f=fase_stap.naam, s=stap.naam,
                                                              fid=fase_stap.id, did=None, sid=stap.id))
    logging.info('End Application')
