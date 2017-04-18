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
from sqlalchemy.orm.exc import NoResultFound


def count_recs_added(db, combi_recs):
    current_recs = db.query(OmerCombi).count()
    recs_added = current_recs - combi_recs
    combi_recs = current_recs
    logging.info("{ra} Records toegevoegd".format(ra=recs_added))
    return combi_recs


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get connection to the Postgres database
    omdb = omer.Datastore(cfg)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])

    # Get Samenstellen Dossier - Handeling-Voorwerp (Green Path)
    logging.info("Samenstellen Dossier - Handeling - Voorwerp")
    (upfase_id,) = cons_sess.query(UpFase.id).filter_by(code='AANVRAAG_SAMENSTELLEN').one()
    (upgebeurtenis_id,) = cons_sess.query(UpGebeurtenis.id).filter_by(code='STARTEN_NIEUW_DOSSIER').one()
    recs = omdb.samenstellen_han_vwp()
    for rec in recs:
        (uptype_id,) = cons_sess.query(UpType.id).filter_by(code=rec.uptype_code).one()
        query = cons_sess.query(UpDocument.id).filter_by(code=rec.updocument_code)
        (updocument_id,) = query.filter_by(source='dossierstuk').one()
        combi_dict = dict(
            uptype_id=uptype_id,
            upfase_id=upfase_id,
            upgebeurtenis_id=upgebeurtenis_id,
            updocument_id=updocument_id
        )
        if not cons_sess.query(OmerCombi).filter_by(**combi_dict).first():
            cons_sess.add(OmerCombi(**combi_dict))
    cons_sess.commit()
    tot_recs = count_recs_added(cons_sess, 0)

    # Get Samenstellen Dossier - Functie (Blue Path)
    logging.info("Samenstellen Dossier - Handeling - Voorwerp - Functie")
    recs = omdb.samenstellen_han_vwp_functie()
    for rec in recs:
        (uptype_id,) = cons_sess.query(UpType.id).filter_by(code=rec.uptype_code).one()
        query = cons_sess.query(UpDocument.id).filter_by(code=rec.updocument_code)
        try:
            (updocument_id,) = query.filter_by(source='datablok').one()
        except NoResultFound:
            logging.error("Datablok {db} not found (Type {dt})".format(dt=rec.uptype_code, db=rec.updocument_code))
        else:
            combi_dict = dict(
                uptype_id=uptype_id,
                upfase_id=upfase_id,
                upgebeurtenis_id=upgebeurtenis_id,
                updocument_id=updocument_id
            )
            if not cons_sess.query(OmerCombi).filter_by(**combi_dict).first():
                cons_sess.add(OmerCombi(**combi_dict))
    cons_sess.commit()
    tot_recs = count_recs_added(cons_sess, tot_recs)

    # Get Samenstellen Dossier - Vaste Documenten (Lila Path)
    logging.info("Samenstellen Dossier - Vaste documenten")
    recs = omdb.samenstellen_vast()
    for rec in recs:
        (uptype_id,) = cons_sess.query(UpType.id).filter_by(code=rec.uptype_code).one()
        query = cons_sess.query(UpDocument.id).filter_by(code=rec.updocument_code)
        (updocument_id,) = query.filter_by(source='dossierstuk').one()
        combi_dict = dict(
            uptype_id=uptype_id,
            upfase_id=upfase_id,
            upgebeurtenis_id=upgebeurtenis_id,
            updocument_id=updocument_id
        )
        if not cons_sess.query(OmerCombi).filter_by(**combi_dict).first():
            cons_sess.add(OmerCombi(**combi_dict))
    cons_sess.commit()
    tot_recs = count_recs_added(cons_sess, tot_recs)

    # Get Samenstellen Dossier - Milieuvergunning (Yellow Path)
    logging.info("Samenstellen Dossier - Milieuvergunning")
    recs = omdb.samenstellen_milieu_projecttype()
    for rec in recs:
        (uptype_id,) = cons_sess.query(UpType.id).filter_by(code=rec.uptype_code).one()
        query = cons_sess.query(UpDocument.id).filter_by(code=rec.updocument_code)
        (updocument_id,) = query.filter_by(source='dossierstuk').one()
        combi_dict = dict(
            uptype_id=uptype_id,
            upfase_id=upfase_id,
            upgebeurtenis_id=upgebeurtenis_id,
            updocument_id=updocument_id
        )
        if not cons_sess.query(OmerCombi).filter_by(**combi_dict).first():
            cons_sess.add(OmerCombi(**combi_dict))
    cons_sess.commit()
    tot_recs = count_recs_added(cons_sess, tot_recs)

    # Get Proces Dossier (Orange Path)
    logging.info("Proces Dossiers")
    recs = omdb.proces_type_docs()
    for rec in recs:
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
    tot_recs = count_recs_added(cons_sess, tot_recs)

    logging.info('End Application')
