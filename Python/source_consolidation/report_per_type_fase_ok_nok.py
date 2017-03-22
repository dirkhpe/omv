"""
This script will create two reports per dossiertype. One report is with data that is complete, the other report is with
data that is not complete and requires review.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

# import logging
from lib import my_env
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

    :return: List of translations.
    """
    list_tx = []
    if prev_comp != not_translated:
        for upcomps in cons_sess.query(arcomp).filter_by(id=comp_id).filter(arcomp.upcomps.any()):
            for upcomp in upcomps.upcomps:
                list_tx.append(upcomp.naam)
    if len(list_tx) == 0:
        list_tx.append(not_translated)
    return list_tx


def list_of_gebeurtenis(arcomp, comp_id, prev_comp=None):
    """
    This function will get all the translations for this specific arstap to upstap, then to gebeurtenis.
    I know that each arstap translates to exactly one upstap. Each upstap translates to many gebeurtenissen.

    :param arcomp: Class for the Archief Component. This is always ArStap in this case.

    :param comp_id: ID for the Archief component arstap

    :param prev_comp: If previous component is not translated, then this component does not need to be translated

    :return: List of translations.
    """
    list_tx = []
    if prev_comp != not_translated:
        # Get my upstap name for this arstap
        f_arstap = cons_sess.query(arcomp).filter_by(id=comp_id).filter(arcomp.upcomps.any()).one()
        f_upstap = f_arstap.upcomps[0]
        for gebeurtenissen in cons_sess.query(UpStap).filter_by(id=f_upstap.id).filter(UpStap.gebeurtenissen.any()):
            for gebeurtenis in gebeurtenissen.gebeurtenissen:
                # list_tx.append("{s};{g}".format(s=upstap, g=gebeurtenis.naam))
                list_tx.append(gebeurtenis.naam)
    if len(list_tx) == 0:
        list_tx.append(not_translated)
    # logging.info("{s}: {g}".format(s=upstap_naam, g=list_tx))
    return list_tx


def propose_document():
    """
    This method will verify if the result line is with missing document only.
    If so, remember the line for a report on missing documents, with a proposal on where they need to be added.
    :return:
    """
    if upstap != not_translated:
        # OK - document is the only item that is not translated, so remember
        prop_line = "{ardoc};{uptype};{upfase};{upgebeurtenis}\n".format(ardoc=ardocument.naam, uptype=uptype,
                                                                         upfase=upfase, upgebeurtenis=upstap)
        if prop_line not in prop_lines:
            prop_lines.append(prop_line)
            # logging.info("Doc Prop added, total lenth: {l}".format(l=len(prop_lines)))
    return


if __name__ == "__main__":

    cfg = my_env.init_env("convert_protege", __file__)

    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"],
                                   echo=False)

    fn_stats = os.path.join(cfg['Main']['reportdir'], "{fn} Fase.csv".format(fn='Statistieken'))
    fh_stats = open(fn_stats, 'w')
    stats_line = "Dossiertype;Fase;Records;Duplicates;OK;Review\n"
    fh_stats.write(stats_line)

    for artype in cons_sess.query(ArType).filter(ArType.fases.any()):
        # Find Fase, Stap / Gebeurtenis and Document
        for uptype in list_of_tx(ArType, artype.id):
            for arfase in artype.fases:
                fase_decreet, fase_besluit = my_env.get_artikels(cons_sess, ArFase, arfase.id)
                for upfase in list_of_tx(ArFase, arfase.id, prev_comp=uptype):

                    # Initialize Files and Statistics
                    fase_naam = "{ar}".format(ar=arfase.naam)
                    fn = "{type} - {fase}".format(type=artype.naam, fase=fase_naam)
                    fn_ok = os.path.join(cfg['Main']['reportdir'], "{fn}.csv".format(fn=fn))
                    fn_nok = os.path.join(cfg['Main']['reportdir'], "{fn} (review).csv".format(fn=fn))
                    with open(fn_ok, 'w') as fh_ok:
                        with open(fn_nok, 'w') as fh_nok:
                            report_lines = []
                            dup_cnt = 0
                            fh_ok_cnt = 0
                            fh_nok_cnt = 0
                            title_line = "Artikels;;Archief;;;Uitwisselingsplatform\n"
                            fh_ok.write(title_line)
                            fh_nok.write(title_line)
                            title_line = "decreet;besluit;stap;document;;gebeurtenis;document\n"
                            fh_ok.write(title_line)
                            fh_nok.write(title_line)

                            for arstap2fase in cons_sess.query(ArFase).filter_by(id=arfase.id)\
                                    .filter(ArFase.stappen.any()):
                                for arstap in arstap2fase.stappen:
                                    stap_decreet, stap_besluit = my_env.get_artikels(cons_sess, ArStap, arstap.id)
                                    for upstap in list_of_gebeurtenis(ArStap, arstap.id, prev_comp=upfase):
                                        for ardocument2stap in cons_sess.query(ArStap).filter_by(id=arstap.id)\
                                                .filter(ArStap.documenten.any()):
                                            for ardocument in ardocument2stap.documenten:
                                                doc_decreet, doc_besluit = my_env.get_artikels(cons_sess, ArDocument,
                                                                                               ardocument.id)
                                                decreet = my_env.format_artikels(doc_decreet + stap_decreet +
                                                                                 fase_decreet)
                                                besluit = my_env.format_artikels(doc_besluit + stap_besluit +
                                                                                 fase_besluit)
                                                for updocument in list_of_tx(ArDocument, ardocument.id,
                                                                             prev_comp=upstap):
                                                    rl = "{decreet};{besluit};{s};{ardoc};;{upstap};{updoc}\n" \
                                                          .format(s=arstap.naam,
                                                                  ardoc=ardocument.naam,
                                                                  upstap=upstap,
                                                                  updoc=updocument, decreet=decreet, besluit=besluit)
                                                    if rl in report_lines:
                                                        dup_cnt += 1
                                                    else:
                                                        if not_translated in rl:
                                                            # Add line for review
                                                            fh_nok.write(rl)
                                                            fh_nok_cnt += 1
                                                            # Check if this is a document only issue
                                                            propose_document()
                                                        else:
                                                            # All information available, line is OK!
                                                            fh_ok.write(rl)
                                                            fh_ok_cnt += 1
                                                        report_lines.append(rl)
                    logging.warning("{type} - {fase} - Found {l} records, {dc} duplicates not included. "
                                    "{ok} Records OK, {nok} Records for review"
                                    .format(type=artype.naam, fase=fase_naam, l=len(report_lines),
                                            dc=dup_cnt, ok=fh_ok_cnt, nok=fh_nok_cnt))
                    stats_line = "{type};{fase};{l};{dc};{ok};{nok}\n"\
                        .format(type=artype.naam, fase=fase_naam, l=len(report_lines),
                                dc=dup_cnt, ok=fh_ok_cnt, nok=fh_nok_cnt)
                    fh_stats.write(stats_line)

    fh_stats.close()

    # Now write for every document a list of proposed values
    prop_lines.sort()
    fn = os.path.join(cfg['Main']['reportdir'], "Voorstel Documenten.csv")
    with open(fn, 'w') as fh:
        title_line = "Document;Type;Fase;Gebeurtenis\n"
        fh.write(title_line)
        for line in prop_lines:
            fh.write(line)


logging.info('End Application')
