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


def get_artikels(link, source_id):
    """
    This function will collect all Wet Artikels linked to Source ID for class link
    @param link: Link Object: Type2Artikel, Fase2Artikel, Stap2Artikel or Document2Artikel
    @param source_id: ID of the Source object (Type, Fase, Stap or Document
    @return: list of WetArtikels
    """
    decreet_list = []
    besluit_list = []
    for record in cons_sess.query(link).filter_by(id=source_id).filter(link.artikels.any()):
        for artikel in record.artikels:
            if artikel.toc.boek.naam == 'Decreet':
                decreet_list.append(artikel.artikel)
            elif artikel.toc.boek.naam == 'Uitvoeringsbesluit':
                besluit_list.append(artikel.artikel)
            else:
                logging.error("Boek *{b}* not found for Class {c} and ID {id}".format(b=artikel.toc.boek.naam,
                                                                                      c=link.__name__,
                                                                                      id=source_id))
    return decreet_list, besluit_list


def format_artikels(artikel_list):
    clean_list = [str(x) for x in sorted(list(set(artikel_list)))]
    clean_str = ", ".join(clean_list)
    return clean_str


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"],
                                   echo=False)
    fn = os.path.join(cfg['Main']['reportdir'], "sql_dn3.csv")
    fh = open(fn, 'w')
    fh.write("aanleg;procedure;procedurestap;decreet;besluit\n")
    for dossier in cons_sess.query(ArType).filter(ArType.fases.any()):
        type_decreet, type_besluit = get_artikels(ArType, dossier.id)
        for fase in dossier.fases:
            fase_decreet, fase_besluit = get_artikels(ArFase, fase.id)
            for fase_stap in cons_sess.query(ArFase).filter_by(id=fase.id).filter(ArFase.stappen.any()):
                for stap in fase_stap.stappen:
                    stap_decreet, stap_besluit = get_artikels(ArStap, stap.id)
                    decreet = format_artikels(stap_decreet + fase_decreet + type_decreet)
                    besluit = format_artikels(stap_besluit + fase_besluit + type_besluit)
                    fh.write("{f};{d};{s};{decreet};{besluit}\n".format(d=dossier.naam, f=fase.naam, s=stap.naam,
                                                                        decreet=decreet, besluit=besluit))
    fh.close()
    fn = os.path.join(cfg['Main']['reportdir'], "sql_dn4.csv")
    fh = open(fn, 'w')
    fh.write("aanleg;procedure;procedurestap;document;decreet;besluit\n")
    for dossier in cons_sess.query(ArType).filter(ArType.fases.any()):
        type_decreet, type_besluit = get_artikels(ArType, dossier.id)
        for fase in dossier.fases:
            fase_decreet, fase_besluit = get_artikels(ArFase, fase.id)
            for fase_stap in cons_sess.query(ArFase).filter_by(id=fase.id).filter(ArFase.stappen.any()):
                for stap in fase_stap.stappen:
                    stap_decreet, stap_besluit = get_artikels(ArStap, stap.id)
                    for stap_doc in cons_sess.query(ArStap).filter_by(id=stap.id).filter(ArStap.documenten.any()):
                        for doc in stap_doc.documenten:
                            doc_decreet, doc_besluit = get_artikels(ArDocument, doc.id)
                            decreet = format_artikels(doc_decreet + stap_decreet + fase_decreet + type_decreet)
                            besluit = format_artikels(doc_besluit + stap_besluit + fase_besluit + type_besluit)
                            fh.write("{f};{d};{s};{doc};{decreet};{besluit}\n"
                                     .format(d=dossier.naam, f=my_env.aanleg(fase.naam), s=stap.naam, doc=doc.naam,
                                             decreet=decreet, besluit=besluit))
    fh.close()

logging.info('End Application')
