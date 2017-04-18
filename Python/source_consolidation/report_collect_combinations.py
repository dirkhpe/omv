"""
This script will collect the different combinations of dossiertype - fase - gebeurtenis - document.
The result is written to a csv file for manual processing.
This report will have unique combinations per source, so it may have more information then collect_combinations.py
script that writes the information to a database file for automated processing.
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
from lib import write2excel
from lib.mysqlstore import *


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get connection to the Postgres database
    omdb = omer.Datastore(cfg)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])

    fn_stats = os.path.join(cfg['Main']['reportdir'], "{fn} - Stats.csv".format(fn=my_env.get_modulename(__file__)))
    fn_ok = os.path.join(cfg['Main']['reportdir'], "Consolidatie DossierType Document.xlsx")
    for fn in [fn_stats, fn_ok]:
        try:
            if os.path.isfile(fn):
                os.remove(fn)
        except PermissionError:
            logging.fatal("{fn} is open. Close the file(s) and restart...".format(fn=fn))
            sys.exit(1)
    ws = write2excel.Write2Excel()
    ws.init_sheet_cons('Consolidatie')

    # Get Samenstellen Dossier - Handeling-Voorwerp (Green Path)
    logging.info("Samenstellen Dossier - Handeling - Voorwerp")
    bron = 'HanVwp'
    d_type = 'dossierstuk'
    # Initializeren Fase en Gebeurtenis op vaste waarden
    upfase = cons_sess.query(UpFase).filter_by(code='AANVRAAG_SAMENSTELLEN').one()
    upgebeurtenis = cons_sess.query(UpGebeurtenis).filter_by(code='STARTEN_NIEUW_DOSSIER').one()
    recs = omdb.samenstellen_han_vwp()
    for rec in recs:
        combi_dict = dict(
            bron=bron,
            dt_code=rec.uptype_code,
            dt_naam=rec.uptype_naam,
            f_code=upfase.code,
            f_naam=upfase.naam,
            g_code=upgebeurtenis.code,
            g_naam=upgebeurtenis.naam,
            d_type=d_type,
            d_code=rec.updocument_code,
            d_naam=rec.updocument_naam
        )
        ws.write_line_report_combis(combi_dict)
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=len(recs)))

    # Get Samenstellen Dossier - Functie (Blue Path)
    logging.info("Samenstellen Dossier - Handeling - Voorwerp - Functie")
    bron = 'HanVwpFun'
    d_type = 'datablok'
    recs = omdb.samenstellen_han_vwp_functie()
    for rec in recs:
        combi_dict = dict(
            bron=bron,
            dt_code=rec.uptype_code,
            dt_naam=rec.uptype_naam,
            f_code=upfase.code,
            f_naam=upfase.naam,
            g_code=upgebeurtenis.code,
            g_naam=upgebeurtenis.naam,
            d_type=d_type,
            d_code=rec.updocument_code,
            d_naam=rec.updocument_naam
        )
        ws.write_line_report_combis(combi_dict)
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=len(recs)))

    # Get Samenstellen Dossier - Vaste Documenten (Lila Path)
    logging.info("Vast")
    bron = 'Samenstellen - Vast'
    d_type = 'dossierstuk'
    recs = omdb.samenstellen_vast()
    for rec in recs:
        combi_dict = dict(
            bron=bron,
            dt_code=rec.uptype_code,
            dt_naam=rec.uptype_naam,
            f_code=upfase.code,
            f_naam=upfase.naam,
            g_code=upgebeurtenis.code,
            g_naam=upgebeurtenis.naam,
            d_type=d_type,
            d_code=rec.updocument_code,
            d_naam=rec.updocument_naam
        )
        ws.write_line_report_combis(combi_dict)
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=len(recs)))

    # Get Samenstellen Dossier - Milieuvergunning (Yellow Path)
    logging.info("Samenstellen Dossier - Milieuvergunning")
    bron = 'Milieu'
    d_type = 'dossierstuk'
    recs = omdb.samenstellen_milieu_projecttype()
    for rec in recs:
        combi_dict = dict(
            bron=bron,
            dt_code=rec.uptype_code,
            dt_naam=rec.uptype_naam,
            f_code=upfase.code,
            f_naam=upfase.naam,
            g_code=upgebeurtenis.code,
            g_naam=upgebeurtenis.naam,
            d_type=d_type,
            d_code=rec.updocument_code,
            d_naam=rec.updocument_naam
        )
        ws.write_line_report_combis(combi_dict)
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=len(recs)))

    # Get Proces Dossier (Orange Path)
    logging.info("Proces Dossiers")
    bron = 'Behandelen'
    recs = omdb.proces_type_docs()
    for rec in recs:
        if rec.updocument_code:
            d_type = 'dossierstuk'
            updocument_code = rec.updocument_code
            updocument_naam = rec.updocument_naam
        else:
            d_type = 'datablok'
            updocument_code = rec.datablok_code
            updocument_naam = rec.datablok_naam
        combi_dict = dict(
            bron=bron,
            dt_code=rec.uptype_code,
            dt_naam=rec.uptype_naam,
            f_code=rec.upfase_code,
            f_naam=rec.upfase_naam,
            g_code=rec.upgebeurtenis_code,
            g_naam=rec.upgebeurtenis_naam,
            d_type=d_type,
            d_code=updocument_code,
            d_naam=updocument_naam
        )
        ws.write_line_report_combis(combi_dict)
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=len(recs)))

    ws.close_workbook_cons(filename=fn)

    logging.info('End Application')
