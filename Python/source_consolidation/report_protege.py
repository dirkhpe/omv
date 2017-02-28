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
                                   pwd=cfg["ConsolidationDB"]["pwd"],
                                   echo=False)
    fn = os.path.join(cfg['Main']['reportdir'], "sql_dn3.csv")
    fh = open(fn, 'w')
    fh.write("aanleg;procedure;procedurestap\n")
    for dossier in cons_sess.query(ArType).filter(ArType.fases.any()):
        for fase in dossier.fases:
            for fase_stap in cons_sess.query(ArFase).filter_by(id=fase.id).filter(ArFase.stappen.any()):
                for stap in fase_stap.stappen:
                    fh.write("{f};{d};{s}\n".format(d=dossier.naam, f=fase.naam, s=stap.naam))
    fh.close()
    fn = os.path.join(cfg['Main']['reportdir'], "sql_dn4.csv")
    fh = open(fn, 'w')
    fh.write("aanleg;procedure;procedurestap;document\n")
    for dossier in cons_sess.query(ArType).filter(ArType.fases.any()):
        for fase in dossier.fases:
            for fase_stap in cons_sess.query(ArFase).filter_by(id=fase.id).filter(ArFase.stappen.any()):
                for stap in fase_stap.stappen:
                    for stap_doc in cons_sess.query(ArStap).filter_by(id=stap.id).filter(ArStap.documenten.any()):
                        for doc in stap_doc.documenten:
                            fh.write("{f};{d};{s};{doc}\n"
                                     .format(d=dossier.naam, f=my_env.aanleg(fase.naam), s=stap.naam, doc=doc.naam))
    fh.close()

logging.info('End Application')
