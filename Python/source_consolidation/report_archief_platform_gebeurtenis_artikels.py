"""
This script will report on the data from the 'Regelgeving' and any possibility from Uitwisselingsplatform.
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
    not_translated = " . "
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
    not_translated = " . "
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


if __name__ == "__main__":

    cfg = my_env.init_env("convert_protege", __file__)

    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"],
                                   echo=False)

    fn = os.path.join(cfg['Main']['reportdir'], "dn3_archief_platform_gebeurtenis_artikels.csv")
    with open(fn, 'w') as fh:
        fh.write("decreet;besluit;dossiertype;fase;stap;;dossiertype;fase;stap\n")
        for artype in cons_sess.query(ArType).filter(ArType.fases.any()):
            type_decreet, type_besluit = my_env.get_artikels(cons_sess, ArType, artype.id)
            for uptype in list_of_tx(ArType, artype.id):
                for arfase in artype.fases:
                    fase_decreet, fase_besluit = my_env.get_artikels(cons_sess, ArFase, arfase.id)
                    for upfase in list_of_tx(ArFase, arfase.id, prev_comp=uptype):
                        for arstap2fase in cons_sess.query(ArFase).filter_by(id=arfase.id).filter(ArFase.stappen.any()):
                            for arstap in arstap2fase.stappen:
                                stap_decreet, stap_besluit = my_env.get_artikels(cons_sess, ArStap, arstap.id)
                                decreet = my_env.format_artikels(stap_decreet + fase_decreet + type_decreet)
                                besluit = my_env.format_artikels(stap_besluit + fase_besluit + type_besluit)
                                for upstap in list_of_tx(ArStap, arstap.id, prev_comp=upfase):
                                    fh.write("{decreet};{besluit};{d};{f};{s};;{uptype};{upfase};{upstap}\n"
                                             .format(d=artype.naam, f=arfase.naam, s=arstap.naam,
                                                     uptype=uptype, upfase=upfase, upstap=upstap,
                                                     decreet=decreet, besluit=besluit))

    fn = os.path.join(cfg['Main']['reportdir'], "dn4_archief_platform_gebeurtenis_artikels.csv")
    with open(fn, 'w') as fh:
        fh.write("decreet;besluit;dossiertype;fase;stap;document;;dossiertype;fase;gebeurtenis;document\n")
        for artype in cons_sess.query(ArType).filter(ArType.fases.any()):
            type_decreet, type_besluit = my_env.get_artikels(cons_sess, ArType, artype.id)
            for uptype in list_of_tx(ArType, artype.id):
                for arfase in artype.fases:
                    fase_decreet, fase_besluit = my_env.get_artikels(cons_sess, ArFase, arfase.id)
                    for upfase in list_of_tx(ArFase, arfase.id, prev_comp=uptype):
                        for arstap2fase in cons_sess.query(ArFase).filter_by(id=arfase.id).filter(ArFase.stappen.any()):
                            for arstap in arstap2fase.stappen:
                                stap_decreet, stap_besluit = my_env.get_artikels(cons_sess, ArStap, arstap.id)
                                for upstap in list_of_gebeurtenis(ArStap, arstap.id, prev_comp=upfase):
                                    for ardocument2stap in cons_sess.query(ArStap).filter_by(id=arstap.id)\
                                            .filter(ArStap.documenten.any()):
                                        for ardocument in ardocument2stap.documenten:
                                            doc_decreet, doc_besluit = my_env.get_artikels(cons_sess, ArDocument,
                                                                                           ardocument.id)
                                            decreet = my_env.format_artikels(doc_decreet + stap_decreet +
                                                                             fase_decreet + type_decreet)
                                            besluit = my_env.format_artikels(doc_besluit + stap_besluit +
                                                                             fase_besluit + type_besluit)
                                            for updocument in list_of_tx(ArDocument, ardocument.id, prev_comp=upstap):
                                                fh.write("{decreet};{besluit};{d};{f};{s};{ardoc};;{uptype};{upfase};"
                                                         "{upstap};{updoc}\n"
                                                         .format(d=artype.naam, f=arfase.naam, s=arstap.naam,
                                                                 ardoc=ardocument.naam,
                                                                 uptype=uptype, upfase=upfase, upstap=upstap,
                                                                 updoc=updocument, decreet=decreet, besluit=besluit))

logging.info('End Application')
