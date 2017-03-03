"""
This script will get the data from the Postgres 'Uitwisselingsloket'. Source is the Postgres database.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
from lib import my_env
from lib import pg_omv
from lib import mysqlstore as mysql
from lib.mysqlstore import *


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get connection to the Postgres database
    pg = pg_omv.Datastore(cfg)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])
    # Get Dossiertypes from Uitwisselingsplatform: tp_dossierinhouddefinitie
    recs = pg.get_table('tp_dossierinhouddefinitie')
    for rec in recs:
        uptype = UpType(
            code=rec.code,
            naam=rec.omschrijving_kort
        )
        cons_sess.add(uptype)
    # Get Fase from Uitwisselingsplatform: tp_fase:
    recs = pg.get_table('tp_fase')
    for rec in recs:
        upfase = UpFase(
            code=rec.code,
            naam=rec.omschrijving_kort
        )
        cons_sess.add(upfase)
    # Get Gebeurtenis from Uitwisselingsplatform: tp_gebeurtenis:
    recs = pg.get_table('tp_gebeurtenis')
    for rec in recs:
        upgebeurtenis = UpGebeurtenis(
            code=rec.code,
            naam=rec.gebeurtenis
        )
        cons_sess.add(upgebeurtenis)
    # Get Dossierstukken from Uitwisselingsplatform: tp_dossierstuktype
    recs = pg.get_table('tp_dossierstuktype')
    for rec in recs:
        updocumenten = UpDocument(
            code=rec.code,
            naam=rec.dossierstuktype
        )
        cons_sess.add(updocumenten)
    cons_sess.commit()
    logging.info('End Application')
