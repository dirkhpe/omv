"""
This script will import the Excel DataMapping to map information from Uitwisselingsplatform with information from
Archief.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
from collections import namedtuple
from lib import my_env
from lib import mysqlstore as mysql
from lib.mysqlstore import *
from openpyxl import load_workbook


def get_named_row(nr_name, col_hrd):
    """
    This method will create a named tuple row.

    :param nr_name: Name of the Named Row. Worksheet name in this case. This will be helpful in case of errors.

    :param col_hrd: Where the column information is stored.

    :return: namedtuple class with name "named_row"
    """
    # Get column names
    field_list = [cell.value for cell in col_hrd]
    # Create named tuple subclass with name "named_row"
    named_row = namedtuple(nr_name, field_list, rename=True)
    return named_row


if __name__ == "__main__":
    # Configure Command line argumentsb
    cfg = my_env.init_env("convert_protege", __file__)
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])
    # Get Workbook information
    wb = load_workbook(cfg['Main']['cons_excel'], read_only=True)
    # Work on link 'Gebeurtenis - Stap'
    ws = wb['Gebeurtenis']
    # Convert worksheet info to list of rows.
    row_list = list(ws.rows)
    # Get name tuple from title row
    title_row = row_list.pop(0)
    nr = get_named_row('Gebeurtenis', title_row)
    stappen = {}
    for row in map(nr._make, row_list):
        # New procedurestap to be added to table upstappen?
        stap = row.ProcedureStap.value
        gebeurtenis_code = row.code.value
        try:
            stap_id = stappen[stap]
        except KeyError:
            # New procedurestap, add to table upstappen!
            upstap = UpStap(
                naam=stap
            )
            cons_sess.add(upstap)
            cons_sess.flush()
            stappen[stap] = upstap.id
            stap_id = stappen[stap]
        # Get Gebeurtenis ID
        gebeurtenis = cons_sess.query(UpGebeurtenis).filter_by(code=gebeurtenis_code).one()
        gebeurtenis_id = gebeurtenis.id
        gebeurtenis2stap = UpGebeurtenis2UpStap(
            upgebeurtenis_id=gebeurtenis_id,
            upstap_id=stap_id
        )
        cons_sess.add(gebeurtenis2stap)
    cons_sess.flush()
    # Then work on Fases
    ws = wb['Fase']
    # Convert worksheet info to list of rows.
    row_list = list(ws.rows)
    # Get name tuple from title row
    title_row = row_list.pop(0)
    nr = get_named_row('Fase', title_row)
    fases = {}
    for row in map(nr._make, row_list):
        fase_naam = row.fase.value
        protege_id = row.protege_id.value
        try:
            upfase_id = fases[fase_naam]
        except KeyError:
            upfase = cons_sess.query(UpFase).filter_by(naam=fase_naam).one()
            fases[fase_naam] = upfase.id
            upfase_id = fases[fase_naam]
        arfase = cons_sess.query(ArFase).filter_by(protege_id=protege_id).one()
        arfase_id = arfase.id
        arfase2upfase = ArFase2UpFase(
            arfase_id=arfase_id,
            upfase_id=upfase_id
        )
        cons_sess.add(arfase2upfase)
    cons_sess.flush()
    # Then work on Dossiertype
    ws = wb['Dossiertype']
    # Convert worksheet info to list of rows.
    row_list = list(ws.rows)
    # Get name tuple from title row
    title_row = row_list.pop(0)
    # In this case title row is on the second row.
    title_row = row_list.pop(0)
    nr = get_named_row('Dossiertype', title_row)
    types = {}
    for row in map(nr._make, row_list):
        if row.code.value:
            code_naam = row.code.value
            ar_naam = row.Archief.value
            try:
                uptype_id = types[code_naam]
            except KeyError:
                uptype = cons_sess.query(UpType).filter_by(code=code_naam).one()
                types[code_naam] = uptype.id
                uptype_id = types[code_naam]
            artype = cons_sess.query(ArType).filter_by(naam=ar_naam)
            artype_id = artype.id
            artype2uptype = ArType2UpType(
                artype_id=artype_id,
                uptype_id=uptype_id
            )
            cons_sess.add(artype2uptype)
    cons_sess.commit()
    logging.info('End Application')
