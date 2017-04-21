"""
This script will get the regelgeving artikels from the 'Regelgeving'. Source is Protege, data is available in sqlite
store.
First load the Artikels and link them to the TOC (wettoc).
Then find procedure artefacts (dossiertype, fase, stap, document) and link artikels.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

# import logging
from lib import my_env
from lib import sqlite_al as sqlite
from lib.sqlite_al import Component, Relation
from lib import mysqlstore as mysql
from lib.mysqlstore import *


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get session for Regelgeving Database
    pt_sess = sqlite.init_session(cfg["Main"]["db"])
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])
    # Get Wet Artikels from Regelgeving
    protege_ids = {}
    for comp in pt_sess.query(Component).filter_by(category='Regelgeving_Item'):
        # Find toc in table wettoc
        toc = cons_sess.query(WetToc).filter_by(
            titel=comp.titel_item,
            hoofdstuk=comp.hoofdstuk,
            afdeling=comp.afdeling,
            onderafdeling=comp.onderafdeling
        ).one()
        if toc:
            artikel = WetArtikel(
                toc_id=toc.id,
                artikel=comp.artikel
            )
            cons_sess.add(artikel)
            cons_sess.flush()
            protege_ids[comp.protege_id] = artikel.id
        else:
            logging.error("TOC {t}.{h}.{a}.{o} not found for Artikel {i}"
                          .format(t=comp.titel_item,
                                  h=comp.hoofdstuk,
                                  a=comp.afdeling,
                                  o=comp.onderafdeling,
                                  i=comp.artikel))
    cons_sess.commit()
    # Link Wet Artikels with Proces Artefacts.
    # Collect items per category
    categories = dict(
        ArType=Type2Artikel,
        ArFase=Fase2Artikel,
        ArStap=Stap2Artikel,
        ArDocument=Document2Artikel
    )
    comp_cat = {}
    for cat in categories.keys():
        cat_class = eval(cat)
        for (protege_id,) in cons_sess.query(cat_class.protege_id):
            comp_cat[protege_id] = categories[cat]
    # Now collect all 'beschreven_in' relations from the Relations tabel.
    for rel in pt_sess.query(Relation).filter_by(rel_type='beschreven_in'):
        # Ignore components of category 'Gebeurtenis'.
        if rel.source_comp.category != 'Gebeurtenis':
            obj_class = comp_cat[rel.source]
            obj_inst = obj_class(
                protege_id=rel.source,
                artikel_id=protege_ids[rel.target]
            )
            cons_sess.add(obj_inst)
    cons_sess.commit()
    logging.info('End Application')
