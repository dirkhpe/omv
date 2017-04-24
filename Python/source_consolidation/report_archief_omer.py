"""
This script starts from Archief and consolidates the OMER information.
This script will create two excel workbooks. One workbook has a tab per procedure with full information (stap - document
- gebeurtenis). The goal is for the business to review what is available.
The second workbook has a tab per procedure with incomplete information. The goal is to discuss this list with the
business and complete the missing information.
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


def list_of_tx(arcomp, comp_id, prev_comp=None):
    """
    This function will get all the translations for a specific Archief component. In case there is one or more
    translation in the Uitwisselingsplatform, a list of all translations will be provided.
    In case there is no translation, then a list with a single value (" . ") will be provided. This way we are sure
    that the Archief Component is listed.

    :param arcomp: Class for the Archief Component (ArType, ArFase, ArStap, ArDocument)

    :param comp_id: ID for the Archief component

    :param prev_comp: If previous component is not translated, then this component does not need to be translated

    :return: List of translations in tuple (name, ID).
    """
    list_tx = []
    if prev_comp != not_translated:
        for upcomps in cons_sess.query(arcomp).filter_by(id=comp_id).filter(arcomp.upcomps.any()):
            for upcomp in upcomps.upcomps:
                list_tx.append((upcomp.naam, upcomp.id))
    if len(list_tx) == 0:
        list_tx.append((not_translated, None))
    return list_tx


def propose_document():
    """
    This method will verify if the result line is with missing document only.
    If so, remember the line for a report on missing documents, with a proposal on where they need to be added.
    :return:
    """
    if gebeurtenis != not_translated:
        # OK - document is the only item that is not translated, so remember
        prop_line = "{ardoc};{uptype};{upfase};{upgebeurtenis}\n".format(ardoc=ardocument.naam, uptype=uptype,
                                                                         upfase=upfase, upgebeurtenis=gebeurtenis)
        if prop_line not in prop_lines:
            prop_lines.append(prop_line)
            # logging.info("Doc Prop added, total lenth: {l}".format(l=len(prop_lines)))
    return


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
    repname = "Archief Combinataties"
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
    stats_line = "Dossiertype;Fase;Records;Duplicates;OK;Review\n"
    fh_stats.write(stats_line)

    for artype in cons_sess.query(ArType).filter(ArType.fases.any()).order_by(ArType.naam):

        # Each Type goes to a new tab in the workbook.
        ws_ok.init_sheet(title=tx_type[artype.naam.lower()])
        ws_nok.init_sheet(title=tx_type[artype.naam.lower()])

        # Find Fase, Stap / Gebeurtenis and Document
        for (uptype, _) in list_of_tx(ArType, artype.id):
            for arfase in artype.fases:
                fase_decreet, fase_besluit = my_env.get_artikels(cons_sess, ArFase, arfase.id)
                for (upfase, _) in list_of_tx(ArFase, arfase.id, prev_comp=uptype):

                    # Initialize Files and Statistics

                    report_lines = []
                    dup_cnt = 0
                    fh_ok_cnt = 0
                    fh_nok_cnt = 0

                    for arstap2fase in cons_sess.query(ArFase).filter_by(id=arfase.id).filter(ArFase.stappen.any()):
                        for arstap in arstap2fase.stappen:
                            stap_decreet, stap_besluit = my_env.get_artikels(cons_sess, ArStap, arstap.id)
                            for ardocument2stap in cons_sess.query(ArStap).filter_by(id=arstap.id)\
                                    .filter(ArStap.documenten.any()):
                                for ardocument in ardocument2stap.documenten:
                                    doc_decreet, doc_besluit = my_env.get_artikels(cons_sess, ArDocument,
                                                                                   ardocument.id)
                                    decreet = my_env.format_artikels(doc_decreet + stap_decreet + fase_decreet)
                                    besluit = my_env.format_artikels(doc_besluit + stap_besluit + fase_besluit)
                                    for (updocument, updoc_id) in list_of_tx(ArDocument,
                                                                             ardocument.id, prev_comp=upfase):
                                        for (gebeurtenis, _) in list_of_tx(UpDocument, updoc_id, prev_comp=updocument):
                                            rl_dict = dict(arstap=arstap.naam,
                                                           ardoc=ardocument.naam,
                                                           gebeurtenis=gebeurtenis,
                                                           updoc=updocument,
                                                           decreet=decreet,
                                                           besluit=besluit,
                                                           arfase=arfase.naam)
                                            rl = [rl_dict[k] for k in list(rl_dict)]
                                            if rl in report_lines:
                                                dup_cnt += 1
                                            else:
                                                if not_translated in rl:
                                                    # Add line for review
                                                    ws_nok.write_line(rl_dict)
                                                    fh_nok_cnt += 1
                                                    # Check if this is a document only issue
                                                    propose_document()
                                                else:
                                                    # All information available, line is OK!
                                                    ws_ok.write_line(rl_dict)
                                                    fh_ok_cnt += 1
                                                report_lines.append(rl)

                    logging.warning("{type} - {fase} - Found {l} records, {dc} duplicates not included. "
                                    "{ok} Records OK, {nok} Records for review"
                                    .format(type=artype.naam, fase=arfase.naam,
                                            l=len(report_lines), dc=dup_cnt, ok=fh_ok_cnt, nok=fh_nok_cnt))
                    stats_line = "{type};{fase};{l};{dc};{ok};{nok}\n"\
                        .format(type=artype.naam, fase=arfase.naam, l=len(report_lines),
                                dc=dup_cnt, ok=fh_ok_cnt, nok=fh_nok_cnt)
                    fh_stats.write(stats_line)

    fh_stats.close()
    ws_ok.close_workbook(filename=fn_ok)
    ws_nok.close_workbook(filename=fn_nok)

    # Now write for every document a list of proposed values
    prop_lines.sort()
    fn = os.path.join(cfg['Main']['reportdir'], "Voorstel Documenten.csv")
    with open(fn, 'w') as fh:
        title_line = "Document;Type;Fase;Gebeurtenis\n"
        fh.write(title_line)
        for line in prop_lines:
            fh.write(line)


logging.info('End Application')
