"""
This script will get the data from the 'Regelgeving'. Source is Protege, data is available in sqlite store.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
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
    # Get Dossiertypes from Regelgeving
    protege_ids = {}
    cat2class = dict(
        Dossiertype=ArType,
        ProcedureFase=ArFase,
        ProcedureStap=ArStap,
        Document=ArDocument
    )
    cat2rel = dict(
        voor_dossiertype=ArFase2Type,
        in_procedure=ArStap2Fase,
        bij_procedurestap=ArDocument2Stap
    )
    # First truncate the relations
    for trunc in cat2rel.values():
        cons_sess.query(trunc).delete()
    # Then truncate the component tables
    for trunc in cat2class.values():
        cons_sess.query(trunc).delete()
    for comp in pt_sess.query(Component).filter(Component.category.in_(list(cat2class.keys()))):
        obj_class = cat2class[comp.category]
        obj_inst = obj_class(
            protege_id=comp.protege_id,
            label=comp.label,
            naam=comp.naam,
            commentaar=comp.commentaar,
        )
        cons_sess.add(obj_inst)
        cons_sess.commit()
        protege_ids[comp.protege_id] = obj_inst.id
    # Get relations associated with Dossier items
    for rel in pt_sess.query(Relation).filter(Relation.rel_type.in_(list(cat2rel.keys()))):
        obj_class = cat2rel[rel.rel_type]
        obj_inst = obj_class(
            source_id = protege_ids[rel.source],
            target_id = protege_ids[rel.target]
        )
        cons_sess.add(obj_inst)
        cons_sess.commit()
    logging.info('End Application')
