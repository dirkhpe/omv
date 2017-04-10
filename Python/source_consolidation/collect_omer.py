"""
This script will get the data from the OMER MS Access database 'Uitwisselingsloket'.
The goal is to collect types, fases, gebeurtenissen en documenten / datablokken.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

# import logging
from lib import my_env
from lib import omer
from lib import mysqlstore as mysql
from lib.mysqlstore import *


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get connection to the Postgres database
    omdb = omer.Datastore(cfg)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])
    # Get Dossiertypes from Uitwisselingsplatform: tp_dossierinhouddefinitie
    recs = omdb.get_table('tp_dossierinhouddef')
    for rec in recs:
        uptype = UpType(
            code=rec.dosinh_code,
            naam=rec.dosinh_naamkort
        )
        cons_sess.add(uptype)
    # Get Fase from Uitwisselingsplatform: tp_fase:
    recs = omdb.get_table('tabfase')
    for rec in recs:
        upfase = UpFase(
            code=rec.fase_code,
            naam=rec.fase_naamkort
        )
        cons_sess.add(upfase)
    # Get Gebeurtenis from Uitwisselingsplatform: tp_gebeurtenis:
    recs = omdb.get_table('tabgebeurtenis')
    for rec in recs:
        upgebeurtenis = UpGebeurtenis(
            code=rec.geb_code,
            naam=rec.geb_naam
        )
        cons_sess.add(upgebeurtenis)
    # Get Dossierstukken from Uitwisselingsplatform: tp_dossierstuktype
    recs = omdb.get_table('tabdossierstuk')
    for rec in recs:
        updocumenten = UpDocument(
            code=rec.stuk_code,
            naam=rec.stuk_naam,
            source='dossierstuk'
        )
        cons_sess.add(updocumenten)
    # Get Datablokken from Uitwisselingsplatform and add them to Dossierstukken
    recs = omdb.get_table('tabdatablok')
    for rec in recs:
        # logging.info('Working on record ID {rid}'.format(rid=rec.blok_key))
        updocumenten = UpDocument(
            code=rec.blok_blokid,
            naam=rec.blok_naam,
            source='datablok'
        )
        cons_sess.add(updocumenten)
    cons_sess.commit()
    logging.info('End Application')
