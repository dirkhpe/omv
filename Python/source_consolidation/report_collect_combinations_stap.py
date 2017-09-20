"""
This script will collect the different combinations of dossiertype - fase - gebeurtenis - document.
The result is written to a csv file for manual processing.
This report will have unique combinations per source, so it may have more information then collect_combinations.py
script that writes the information to a database file for automated processing.

This script will add the stap for each gebeurtenis.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

# import logging
from datetime import datetime as dt
from lib import my_env
from lib import omer
from lib import mysqlstore as mysql
from lib import write2excel
from lib.mysqlstore import *


def docblok2array(stuk_code, stuk_naam, b1_code, b1_naam, b2_code, b2_naam):
    res = []
    if stuk_code:
        res.append(['dossierstuk', stuk_code, stuk_naam])
    if b1_code:
        res.append(['datablok', b1_code, b1_naam])
    if b2_code:
        res.append(['datablok', b2_code, b2_naam])
    return res


if __name__ == "__main__":
    now = dt.now().strftime("%Y%m%d%H%M%S")
    cfg = my_env.init_env("convert_protege", __file__)
    # Get connection to the Postgres database
    omdb = omer.Datastore(cfg)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])

    repname = 'Consolidatie OMER incl Stap'
    fn_stats = os.path.join(cfg['Main']['reportdir'], "Stats {r} {now}.csv".format(r=repname, now=now))
    fn_ok = os.path.join(cfg['Main']['reportdir'], "{r} {now}.xlsx".format(r=repname, now=now))

    for fn in [fn_stats, fn_ok]:
        try:
            if os.path.isfile(fn):
                os.remove(fn)
        except PermissionError:
            logging.fatal("{fn} is open. Close the file(s) and restart...".format(fn=fn))
            sys.exit(1)
    ws = write2excel.Write2Excel()
    ws.init_sheet_cons_stap('Consolidatie_stap')

    fh_stats = open(fn_stats, 'w')
    fh_stats.write("bron;records\n")

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
            s_naam=upgebeurtenis.upstap.naam,
            d_type=d_type,
            d_code=rec.updocument_code,
            d_naam=rec.updocument_naam
        )
        ws.write_line_report_combis_stap(combi_dict)
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=len(recs)))
    fh_stats.write("{b};{ra}\n".format(b=bron, ra=len(recs)))

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
            s_naam=upgebeurtenis.upstap.naam,
            d_type=d_type,
            d_code=rec.updocument_code,
            d_naam=rec.updocument_naam
        )
        ws.write_line_report_combis_stap(combi_dict)
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=len(recs)))
    fh_stats.write("{b};{ra}\n".format(b=bron, ra=len(recs)))

    # Get Samenstellen Dossier - Vaste Documenten (Lila Path)
    logging.info("Vast")
    bron = 'Vast'
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
            s_naam=upgebeurtenis.upstap.naam,
            d_type=d_type,
            d_code=rec.updocument_code,
            d_naam=rec.updocument_naam
        )
        ws.write_line_report_combis_stap(combi_dict)
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=len(recs)))
    fh_stats.write("{b};{ra}\n".format(b=bron, ra=len(recs)))

    # Get Samenstellen Dossier - Milieuvergunning (Yellow Path)
    logging.info("Samenstellen Dossier - Milieuvergunning")
    bron = 'Milieu'
    d_type = 'dossierstuk'
    # recs = omdb.samenstellen_milieu_projecttype()
    recs = omdb.samenstellen_milieu_stuk_blok()
    blok_cnt = 0
    for rec in recs:
        combi_dict = dict(
            bron=bron,
            dt_code=rec.uptype_code,
            dt_naam=rec.uptype_naam,
            f_code=upfase.code,
            f_naam=upfase.naam,
            g_code=upgebeurtenis.code,
            g_naam=upgebeurtenis.naam,
            s_naam=upgebeurtenis.upstap.naam,
            d_type=d_type,
            d_code=rec.updocument_code,
            d_naam=rec.updocument_naam
        )
        ws.write_line_report_combis_stap(combi_dict)
        if rec.blok_blokid:
            # Samenstellen Dossier: dossierstuk EN datablok
            combi_dict['d_type'] = 'datablok'
            combi_dict['d_code'] = rec.blok_blokid
            combi_dict['d_naam'] = rec.blok_naam
            ws.write_line_report_combis_stap(combi_dict)
            blok_cnt += 1
    logging.info("Bron: {b} - {ra} Records toegevoegd ({bc} extra datablokken)"
                 .format(b=bron, ra=len(recs)+blok_cnt, bc=blok_cnt))
    fh_stats.write("{b};{ra}\n".format(b=bron, ra=len(recs)))

    # Get Proces Dossier (Orange Path)
    logging.info("Proces Dossiers")
    bron = 'Behandelen'
    dupl = {}
    # Get all gebeurtenis to stap translations
    gebeurtenis2stap = {}
    upgebeurtenissen = cons_sess.query(UpGebeurtenis).all()
    for g in upgebeurtenissen:
        if g.upstap:
            gebeurtenis2stap[g.code] = g.upstap.naam
        else:
            gebeurtenis2stap[g.code] = 'toch nog niet gedefinieerd'

    # Now get all records
    recs = omdb.process_type_docs_blok()
    blok_cnt = 0
    for rec in recs:
        stap = gebeurtenis2stap[rec.upgebeurtenis_code]
        docblok = docblok2array(rec.updocument_code, rec.updocument_naam,
                                rec.db_blok_code, rec.db_blok_naam,
                                rec.b_blok_code, rec.b_blok_naam)
        for doc in docblok:
            combi_dict = dict(
                bron=bron,
                dt_code=rec.uptype_code,
                dt_naam=rec.uptype_naam,
                f_code=rec.upfase_code,
                f_naam=rec.upfase_naam,
                g_code=rec.upgebeurtenis_code,
                g_naam=rec.upgebeurtenis_naam,
                s_naam=stap,
                d_type=doc[0],
                d_code=doc[1],
                d_naam=doc[2]
            )
            ws.write_line_report_combis_stap(combi_dict)
            blok_cnt += 1
            dupl_key = "{type};{fase};{stap};{doc}".format(type=rec.uptype_code, fase=rec.upfase_code,
                                                           stap=stap, doc=doc[1])
            dupl_val = "{type};{fase};{geb};{doc}".format(type=rec.uptype_code, fase=rec.upfase_code,
                                                          geb=rec.upgebeurtenis_code, doc=doc[1])
            if dupl_key in dupl:
                if not (dupl_val in dupl[dupl_key]):
                    dupl[dupl_key].append(dupl_val)
            else:
                dupl[dupl_key] = [dupl_val]
    logging.info("Bron: {b} - {ra} Records toegevoegd".format(b=bron, ra=blok_cnt))
    fh_stats.write("{b};{ra}\n".format(b=bron, ra=blok_cnt))

    ws.close_workbook_cons_stap(filename=fn_ok)
    fh_stats.close()

    # Now also print duplicates
    fn_dupl = os.path.join(cfg['Main']['reportdir'], "Dupl {r} {now}.csv".format(r=repname, now=now))
    fh_dupl = open(fn_dupl, 'w')
    hdr = "Type;Fase;Stap;Doc;;Type;Fase;Gebeurtenis;Doc\n"
    fh_dupl.write(hdr)
    blok_cnt = 0
    uni_cnt = 0
    for k in dupl:
        if len(dupl[k]) > 1:
            uni_cnt += 1
            for v in dupl[k]:
                fh_dupl.write("{k};;{v}\n".format(k=k, v=v))
                blok_cnt += 1
            fh_dupl.write("\n")
    fh_dupl.close()
    logging.info("{b} duplicates replaces with {u} unique records".format(b=blok_cnt, u=uni_cnt))

    logging.info('End Application')
