"""
This script will collect the different combinations of dossiertype - fase - gebeurtenis - document.

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


def count_recs_added(dbc, combi_recs):
    current_recs = dbc.query(OmerCombi).count()
    recs_added = current_recs - combi_recs
    combi_recs = current_recs
    logging.info("{ra} Records toegevoegd".format(ra=recs_added))
    return combi_recs


def handle_query_res(query_res):
    for rec in query_res:
        (uptype_id,) = cons_sess.query(UpType.id).filter_by(code=rec.uptype_code).one()
        (upfase_id,) = cons_sess.query(UpFase.id).filter_by(code=rec.upfase_code).one()
        (upgebeurtenis_id,) = cons_sess.query(UpGebeurtenis.id).filter_by(code=rec.upgebeurtenis_code).one()
        if rec.updocument_code:
            query = cons_sess.query(UpDocument.id).filter_by(code=rec.updocument_code)
            (updocument_id,) = query.filter_by(source='dossierstuk').one()
        else:
            query = cons_sess.query(UpDocument.id).filter_by(code=rec.datablok_code)
            (updocument_id,) = query.filter_by(source='datablok').one()
        combi_dict = dict(
            uptype_id=uptype_id,
            upfase_id=upfase_id,
            upgebeurtenis_id=upgebeurtenis_id,
            updocument_id=updocument_id
        )
        if not cons_sess.query(OmerCombi).filter_by(**combi_dict).first():
            cons_sess.add(OmerCombi(**combi_dict))
    cons_sess.commit()


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get connection to the Postgres database
    omdb = omer.Datastore(cfg)
    # Get session for Consolidation Database
    db = cfg['ConsolidationDB']['db']
    user = cfg['ConsolidationDB']['user']
    pwd = cfg['ConsolidationDB']['pwd']
    cons_sess = mysql.init_session(db=db,
                                   user=user,
                                   pwd=pwd)

    # Truncate omercombi Table
    direct_conn = mysql.DirectConn(user=user, pwd=pwd)
    direct_conn.truncate_table(db, 'omercombi')
    tot_recs = 0

    # Get Proces Dossier (Orange Path)
    logging.info("Proces Dossiers van DossierFase")
    recs = omdb.proces_docs()
    handle_query_res(recs)
    tot_recs = count_recs_added(cons_sess, tot_recs)

    # Get Proces Dossier (Orange Path)
    logging.info("Proces Dossiers van ProjectType")
    recs = omdb.proces_type_docs()
    handle_query_res(recs)
    tot_recs = count_recs_added(cons_sess, tot_recs)

    # Truncate omercombi Table
    cons_sess.close()
    direct_conn.truncate_table(db, 'omercombi')
    cons_sess = mysql.init_session(db=db,
                                   user=user,
                                   pwd=pwd)
    tot_recs = 0

    # Get Proces Dossier (Orange Path)
    logging.info("Proces Dossiers van ProjectType")
    recs = omdb.proces_type_docs()
    handle_query_res(recs)
    tot_recs = count_recs_added(cons_sess, tot_recs)

    # Get Proces Dossier (Orange Path)
    logging.info("Proces Dossiers van DossierFase")
    recs = omdb.proces_docs()
    handle_query_res(recs)
    tot_recs = count_recs_added(cons_sess, tot_recs)

    direct_conn.close()
    logging.info('End Application')
