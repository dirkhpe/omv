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


def list_of_tx2ar(omcomp, comp_id, prev_comp=None):
    """
    This function will get all the translations for a specific Omer component. In case there is one or more
    translation in the Archief, a list of all translations will be provided.
    In case there is no translation, then a list with a single value (" . ") will be provided. This way we are sure
    that the OMER Component is listed.

    :param omcomp: Class for the OMER Component (UpType, UpFase, UpGebeurtenis, UpDocument)

    :param comp_id: ID for the OMER component

    :param prev_comp: If higher-level component is not translated, then this component does not need to be translated

    :return: List of translations.
    """
    list_tx = []
    if prev_comp != not_translated:
        for arcomps in cons_sess.query(omcomp).filter_by(id=comp_id).filter(omcomp.arcomps.any()):
            for arcomp in arcomps.arcomps:
                list_tx.append(arcomp.naam)
    if len(list_tx) == 0:
        list_tx.append(not_translated)
    return list_tx


def gebeurtenis2stap(gebeurtenis_id, prev_comp=None):
    """
    This function will translate the gebeurtenis to upstap. Then list_of_tx2ar is called for further translation.

    :param gebeurtenis_id: ID of the gebeurtenis

    :param prev_comp: If higher-level component is not translated, then this component does not need to be translated.

    :return:
    """
    if prev_comp != not_translated:
        upgeb = cons_sess.query(UpGebeurtenis).filter_by(id=gebeurtenis_id).one()
        if upgeb.upstap:
            upstap_id = upgeb.upstap.id
            return list_of_tx2ar(UpStap, upstap_id, prev_comp)
    return [not_translated]


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
    fn_stats = os.path.join(cfg['Main']['reportdir'], "{fn} - Stats {now}.csv"
                            .format(fn=my_env.get_modulename(__file__), now=now))
    fn_ok = os.path.join(cfg['Main']['reportdir'], "omer_combis {now}.xlsx".format(now=now))
    fn_nok = os.path.join(cfg['Main']['reportdir'], "omer_combis_check {now}.xlsx".format(now=now))
    for fn in [fn_stats, fn_ok, fn_nok]:
        try:
            if os.path.isfile(fn):
                os.remove(fn)
        except PermissionError:
            logging.fatal("{fn} is open. Close the file(s) and restart...".format(fn=fn))
            sys.exit(1)

    fh_stats = open(fn_stats, 'w')
    stats_line = "Dossiertype;Fase;Records;Duplicates;OK;Review\n"
    fh_stats.write(stats_line)

    # Get translations for DossierType, less than 32 characters to fit as a tab-title.
    tx_type = my_env.get_config_section(cfg, 'DossierType')

    decreet = ''
    besluit = ''
    # First get query based on DossierType
    for uptype in cons_sess.query(UpType).order_by(UpType.naam).all():

        # Each uptype translates to 0 or 1 artypes.
        artypes = list_of_tx2ar(UpType, uptype.id)
        if artypes[0] == not_translated:
            logging.info("DossierType niet gevonden, werk met {dt}".format(dt=uptype.naam))
            ws_title = "{id} {n}".format(id=uptype.id, n=uptype.naam.lower())[:31]
            artype = not_translated
        else:
            artype = artypes[0]
            logging.info("DossierType gevonden, werk met {dt}".format(dt=artype))
            ws_title = tx_type[artype.lower()]

        # Each Type goes to a new tab in the workbook.
        ws_ok.init_sheet(title=ws_title)
        ws_nok.init_sheet(title=ws_title)
        query = cons_sess.query(OmerCombi).filter_by(uptype_id=uptype.id)

        # print("Query: {q}".format(q=str(query)))
        report_lines = []

        for rec in query:
            uptype = rec.uptype.naam
            upfase = rec.upfase.naam
            upgebeurtenis = rec.upgebeurtenis.naam
            updocument = rec.updocument.naam
            for arstap in gebeurtenis2stap(rec.upgebeurtenis.id, upfase):
                for ardoc in list_of_tx2ar(UpDocument, rec.updocument.id, arstap):
                    rl_dict = dict(upfase=upfase,
                                   arstap=arstap,
                                   ardoc=ardoc,
                                   gebeurtenis=upgebeurtenis,
                                   updoc=updocument,
                                   decreet=decreet,
                                   besluit=besluit
                                   )
                    rl = [rl_dict[k].lower() for k in list(rl_dict)]
                    if rl not in report_lines:
                        if not_translated in rl:
                            # Add line for review
                            ws_nok.write_line4omer(rl_dict)
                        else:
                            # All information available, line is OK!
                            ws_ok.write_line4omer(rl_dict)
                            # m = hashlib.md5()
                            # m.update(rl)
                            # logging.debug("{h} - {rl}".format(h=m.hexdigest(), rl=rl_arr))
                        report_lines.append(rl)

    fh_stats.close()
    ws_ok.close_workbook(filename=fn_ok)
    ws_nok.close_workbook(filename=fn_nok)

logging.info('End Application')
