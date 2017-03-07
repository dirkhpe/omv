"""
This script will report on the data from the 'Regelgeving'. It will create the fully denormalized report from
Wetgeving. It will add all Wet Artikels related to the items.
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


if __name__ == "__main__":

    cfg = my_env.init_env("convert_protege", __file__)

    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"],
                                   echo=False)

    fn = os.path.join(cfg['Main']['reportdir'], "sql_dn3.csv")
    with open(fn, 'w') as fh:

        fh.write("aanleg;procedure;procedurestap;decreet;besluit\n")

        for dossier in cons_sess.query(ArType).filter(ArType.fases.any()):
            type_decreet, type_besluit = my_env.get_artikels(cons_sess, ArType, dossier.id)
            for fase in dossier.fases:
                fase_decreet, fase_besluit = my_env.get_artikels(cons_sess, ArFase, fase.id)
                for fase_stap in cons_sess.query(ArFase).filter_by(id=fase.id).filter(ArFase.stappen.any()):
                    for stap in fase_stap.stappen:
                        stap_decreet, stap_besluit = my_env.get_artikels(cons_sess, ArStap, stap.id)
                        decreet = my_env.format_artikels(stap_decreet + fase_decreet + type_decreet)
                        besluit = my_env.format_artikels(stap_besluit + fase_besluit + type_besluit)
                        fh.write("{f};{d};{s};{decreet};{besluit}\n".format(d=dossier.naam, f=fase.naam, s=stap.naam,
                                                                            decreet=decreet, besluit=besluit))

    fn = os.path.join(cfg['Main']['reportdir'], "sql_dn4.csv")
    with open(fn, 'w') as fh:

        fh.write("aanleg;procedure;procedurestap;document;decreet;besluit\n")

        for dossier in cons_sess.query(ArType).filter(ArType.fases.any()):
            type_decreet, type_besluit = my_env.get_artikels(cons_sess, ArType, dossier.id)
            for fase in dossier.fases:
                fase_decreet, fase_besluit = my_env.get_artikels(cons_sess, ArFase, fase.id)
                for fase_stap in cons_sess.query(ArFase).filter_by(id=fase.id).filter(ArFase.stappen.any()):
                    for stap in fase_stap.stappen:
                        stap_decreet, stap_besluit = my_env.get_artikels(cons_sess, ArStap, stap.id)
                        for stap_doc in cons_sess.query(ArStap).filter_by(id=stap.id).filter(ArStap.documenten.any()):
                            for doc in stap_doc.documenten:
                                doc_decreet, doc_besluit = my_env.get_artikels(cons_sess, ArDocument, doc.id)
                                decreet = my_env.format_artikels(doc_decreet + stap_decreet +
                                                                 fase_decreet + type_decreet)
                                besluit = my_env.format_artikels(doc_besluit + stap_besluit +
                                                                 fase_besluit + type_besluit)
                                fh.write("{f};{d};{s};{doc};{decreet};{besluit}\n"
                                         .format(d=dossier.naam, f=my_env.aanleg(fase.naam), s=stap.naam, doc=doc.naam,
                                                 decreet=decreet, besluit=besluit))

    logging.info('End Application')
