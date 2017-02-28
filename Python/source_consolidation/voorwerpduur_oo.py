"""
This script will handle duplicate 'Openbaar Onderzoek' during 'Eerste Aanleg'.
This will be done in steps listed below:
1. Create Stap 'Openbaar Onderzoek bij bekendmaking inspraakprocedure'
2. Get all Documenten from 'Openbaar Onderzoek', link them with new node 'Openbaar Onderzoek bij bekendmaking
    inspraakprocedure'
3. Link new stap with fase 'VoorwerpDuur * Samenstellen Eerste Aanleg'
4. Remove link 'Openbaar Onderzoek' naar 'VoorwerpDuur * Samenstellen Eerste Aanleg'
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
from lib import my_env
from lib import mysqlstore as mysql
from lib.mysqlstore import *


if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])
    # 1. Create Stap 'Openbaar Onderzoek bij bekendmaking inspraakprocedure'
    oo_inspraak = ArStap(
        protege_id='OpenbaarOnderzoekBekendmaking',
        label='Openbaar Onderzoek bij Bekendmaking',
        naam='Openbaar Onderzoek bij Bekendmaking',
        commentaar='Openbaar Onderzoek bij Bekendmaking - Extra stap',
    )
    cons_sess.add(oo_inspraak)
    # 2. Get stap 'Openbaar Onderzoek', get all documenten to link them to oo_inspraak node.
    oo_stap = cons_sess.query(ArStap).filter_by(naam='Openbaar Onderzoek').one()
    for doc in oo_stap.documenten:
        oo_inspraak.documenten.append(doc)
    # 3. Link Stap with Fase 'VoorwerpDuur * Samenstellen Eerste Aanleg'
    voorwerpduur = cons_sess.query(ArFase).filter_by(label='VoorwerpDuur * Samenstellen Eerste Aanleg').one()
    voorwerpduur.stappen.append(oo_inspraak)
    # 4. Remove link 'Openbaar Onderzoek' naar 'VoorwerpDuur * Samenstellen Eerste Aanleg'
    voorwerpduur.stappen.remove(oo_stap)
    cons_sess.commit()
    logging.info('End Application')
