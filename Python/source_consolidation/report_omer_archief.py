"""
This script reports on dossiertype - fase - gebeurtenis - document as found in omer database.
Where possible, translations to components from Archief are done.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

# import logging
import os
from datetime import datetime as dt
from lib import my_env
from lib import write2excel
from lib import mysqlstore as mysql
from lib.mysqlstore import *

not_translated = " . "
prop_lines = []


def list_of_tx2ar(omcomp, comp_id, rel_table=None, prev_comp_id=None):
    """
    This function will get all the translations for a specific Omer component. In case there is one or more
    translation in the Archief, a list of all translations will be provided.
    In case there is no translation, then a list with a single value (" . ") will be provided. This way we are sure
    that the OMER Component is listed.

    :param omcomp: Class for the OMER Component (UpType, UpFase, UpGebeurtenis, UpDocument)

    :param comp_id: ID for the OMER component

    :param rel_table: Archief Relation class (table) from higher level component to required component. None for Type.

    :param prev_comp_id: If higher-level component is not translated, then this component does not need to be
    translated. If the higher-level component is translated, then I need the ID of the higher-level component. This
    (lower-level) component must be in the list of possibilities (arfase2type, arstap2fase, ardocument2stap). The list
    of translations must be the cross-cut of Archief possibilities and Uitwisselingsplatform to Archief possibilities.

    :return: List of translations, in tuples (component ID, component name)
    """
    list_tx = []
    if prev_comp_id != -1:
        # Limit the list of component possibilities. They must be in the Archief possibilities.
        # Limit this list for all components below Type.
        if rel_table:
            qry = cons_sess.query(rel_table).filter_by(target_id=prev_comp_id)
            item_ids = [item.source_id for item in qry.all()]
        for arcomps in cons_sess.query(omcomp).filter_by(id=comp_id).filter(omcomp.arcomps.any()):
            for arcomp in arcomps.arcomps:
                if rel_table:
                    if arcomp.id in item_ids:
                        list_tx.append((arcomp.id, arcomp.naam))
                else:
                    # Relation table does not exist, so must be Type. Accept the translation
                    list_tx.append((arcomp.id, arcomp.naam))
    if len(list_tx) == 0:
        list_tx.append((-1, not_translated))
    return list_tx


def gebeurtenis2stap(gebeurtenis_id, prev_comp_id=None):
    """
    This function will translate the gebeurtenis to upstap and returns a list of upstap_ids that can be used in
    list_of_tx2ar, to go from upstap to arstap.

    :param gebeurtenis_id: ID of the gebeurtenis

    :param prev_comp_id: If higher-level component is not translated, then this component does not need to be
    translated.

    :return: upstap_id associated with the gebeurtenis.



    """
    if prev_comp_id != -1:
        upgeb = cons_sess.query(UpGebeurtenis).filter_by(id=gebeurtenis_id).one()
        if upgeb.upstap:
            return upgeb.upstap.id, upgeb.upstap.naam
    return -1, not_translated


if __name__ == "__main__":

    now = dt.now().strftime("%Y%m%d%H%M%S")

    cfg = my_env.init_env("convert_protege", __file__)

    # Get translations for DossierType, less than 32 characters to fit as a tab-title.
    tx_type = my_env.get_config_section(cfg, 'DossierType')

    # Initialize Workbooks for Review (ws_ok) and for Completion (ws_nok).
    ws_ok = write2excel.Write2Excel()
    ws_nok = write2excel.Write2Excel()

    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"],
                                   echo=False)

    # Set-up files and remove previous version of the file.
    repname = "OMER naar Archief"
    fn_stats = os.path.join(cfg['Main']['reportdir'], "Stats {r} {now}.csv".format(r=repname, now=now))
    fn_ok = os.path.join(cfg['Main']['reportdir'], "{r} Validatie {now}.xlsx".format(r=repname, now=now))
    fn_nok = os.path.join(cfg['Main']['reportdir'], "{r} Ontbrekend {now}.xlsx".format(r=repname, now=now))
    for fn in [fn_stats, fn_ok, fn_nok]:
        try:
            if os.path.isfile(fn):
                os.remove(fn)
        except PermissionError:
            logging.fatal("{fn} is open. Close the file(s) and restart...".format(fn=fn))
            sys.exit(1)

    fh_stats = open(fn_stats, 'w')
    stats_line = "Dossiertype;Records;Duplicates;Behandelen OK;Behandelen Review;Dossier OK;Dossier Review\n"
    fh_stats.write(stats_line)

    # Get translations for DossierType, less than 32 characters to fit as a tab-title.
    tx_type = my_env.get_config_section(cfg, 'DossierType')

    decreet = ''
    besluit = ''
    # First get query based on DossierType
    for uptype in cons_sess.query(UpType).order_by(UpType.naam).all():

        # Each uptype translates to 0 or 1 artypes, so no need to implement for-loop.
        artypes = list_of_tx2ar(UpType, uptype.id)
        if artypes[0][1] == not_translated:
            logging.info("DossierType niet gevonden, werk met {dt}".format(dt=uptype.naam))
            ws_title = "{id} {n}".format(id=uptype.id, n=uptype.naam.lower())[:31]
        else:
            artype = artypes[0][1]
            logging.info("DossierType gevonden, werk met {dt}".format(dt=artype))
            ws_title = tx_type[artype.lower()]

        # Each Type goes to a new tab in the workbook.
        ws_ok.init_sheet(title=ws_title)
        ws_nok.init_sheet(title=ws_title)
        query = cons_sess.query(OmerCombi).filter_by(uptype_id=uptype.id)

        # print("Query: {q}".format(q=str(query)))
        report_lines = []
        dup_cnt = 0
        fh_ok_cnt = 0
        fh_nok_cnt = 0
        fh_ok_dossier_cnt = 0
        fh_nok_dossier_cnt = 0

        for rec in query:
            uptype = rec.uptype.naam
            upfase = rec.upfase.naam
            upgebeurtenis = rec.upgebeurtenis.naam
            updocument = rec.updocument.naam
            # Additional step to get ArFase ID.
            arfases = list_of_tx2ar(UpFase, rec.upfase_id, ArFase2Type, artypes[0][0])
            arfase = arfases[0][1]
            arfase_id = arfases[0][0]
            (upstap_id, upstap_naam) = gebeurtenis2stap(rec.upgebeurtenis.id, upfase)
            for arstap in list_of_tx2ar(UpStap, upstap_id, ArStap2Fase, arfase_id):
                for ardoc in list_of_tx2ar(UpDocument, rec.updocument.id, ArDocument2Stap, arstap[0]):
                    rl_dict = dict(upfase=upfase,
                                   arstap=arstap[1],
                                   ardoc=ardoc[1],
                                   gebeurtenis=upgebeurtenis,
                                   updoc=updocument,
                                   decreet=decreet,
                                   besluit=besluit
                                   )
                    rl = [rl_dict[k].lower() for k in list(rl_dict)]
                    if rl in report_lines:
                        dup_cnt += 1
                    else:
                        if not_translated in rl:
                            # Add line for review
                            ws_nok.write_line4omer(rl_dict)
                            if upgebeurtenis == 'Starten van een nieuw dossier':
                                fh_nok_dossier_cnt += 1
                            else:
                                fh_nok_cnt += 1
                        else:
                            # All information available, line is OK!
                            ws_ok.write_line4omer(rl_dict)
                            if upgebeurtenis == 'Starten van een nieuw dossier':
                                fh_ok_dossier_cnt += 1
                            else:
                                fh_ok_cnt += 1
                        report_lines.append(rl)

        stats_line = "{type};{l};{dc};{ok};{nok};{dok};{dnok}\n"\
            .format(type=ws_title, l=len(report_lines), dc=dup_cnt, ok=fh_ok_cnt, nok=fh_nok_cnt,
                    dok=fh_ok_dossier_cnt, dnok=fh_nok_dossier_cnt)
        fh_stats.write(stats_line)

    fh_stats.close()
    ws_ok.close_workbook(filename=fn_ok)
    ws_nok.close_workbook(filename=fn_nok)

logging.info('End Application')
