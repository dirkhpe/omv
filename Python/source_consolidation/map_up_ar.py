"""
This script will import the Excel DataMapping to map information from Uitwisselingsplatform with information from
Archief.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

from collections import namedtuple
from lib import my_env
from lib import mysqlstore as mysql
from lib.mysqlstore import *
from openpyxl import load_workbook
from sqlalchemy.orm.exc import NoResultFound


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


def handle_gebeurtenis(worksheet):
    """
    This function will handle the worksheet 'gebeurtenis' to populate tables upgebeurtenissen, upstappen and
    upgebeurtenis2upstap.
    @param worksheet: Excel Worksheet with gebeurtenis to stap information.
    @return:
    """
    logging.info("Handling Gebeurtenis")
    # Convert worksheet info to list of rows.
    row_list = list(worksheet.rows)
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
        gebeurtenis.upstap_id = stap_id
    cons_sess.flush()
    return


def handle_fase(worksheet):
    """
    This function will handle the worksheet Fase. It links the fase from Uitwisselingsplatform (UP) with the fase from
    Archief (AR).
    @param worksheet: Pointer to the Fase Worksheet.
    @return:
    """
    logging.info("Handling Fase")
    # Convert worksheet info to list of rows.
    row_list = list(worksheet.rows)
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
    return


def handle_dossiertype(worksheet):
    """
    This procedure will handle the worksheet 'Dossiertype' to link Archief Dossiertypes with the codes from
    Uitwisselingsplatform.
    @param worksheet: Pointer to the Dossiertype worksheet.
    @return:
    """
    logging.info("Handling Dossiertype")
    # Convert worksheet info to list of rows.
    row_list = list(worksheet.rows)
    # Get name tuple from title row
    # In this case title row is on the second row.
    row_list.pop(0)
    title_row = row_list.pop(0)
    nr = get_named_row('Dossiertype', title_row)
    types = {}
    for row in map(nr._make, row_list):
        # Set up connection if both Archief and Code are available:
        if row.Archief.value and row.code.value:
            code_naam = row.code.value
            ar_naam = row.Archief.value
            try:
                uptype_id = types[code_naam]
            except KeyError:
                uptype = cons_sess.query(UpType).filter_by(code=code_naam).one()
                types[code_naam] = uptype.id
                uptype_id = types[code_naam]
            artype = cons_sess.query(ArType).filter_by(naam=ar_naam).one()
            artype_id = artype.id
            artype2uptype = ArType2UpType(
                artype_id=artype_id,
                uptype_id=uptype_id
            )
            cons_sess.add(artype2uptype)
    return


def handle_stappen(worksheet):
    """
    This procedure will handle the worksheet 'Stappen' to link Archief Stappen with the codes from
    Uitwisselingsplatform.
    ProcedureStap 'PROCEDURESTAP NOT FOUND' is not included in the mapping table (otherwise gebeurtenissen will be
    incorrectly linked to ArStappen if 'PROCEDURESTAP NOT FOUND' in both cases.

    :param worksheet: Pointer to the Stappen worksheet.

    :return:
    """
    logging.info("Handling Stappen")
    # Convert worksheet info to list of rows.
    row_list = list(worksheet.rows)
    # Get name tuple from title row
    title_row = row_list.pop(0)
    nr = get_named_row('Stappen', title_row)
    stappen = {}
    for row in map(nr._make, row_list):
        procedurestap = row.ProcedureStap.value
        protege_id = row.protege_id.value
        if procedurestap != 'PROCEDURESTAP NOT FOUND':
            try:
                upstap_id = stappen[procedurestap]
            except KeyError:
                upstap = cons_sess.query(UpStap).filter_by(naam=procedurestap).one()
                stappen[procedurestap] = upstap.id
                upstap_id = stappen[procedurestap]
            arstap = cons_sess.query(ArStap).filter_by(protege_id=protege_id).one()
            arstap_id = arstap.id
            arstap2upstap = ArStap2UpStap(
                arstap_id=arstap_id,
                upstap_id=upstap_id
            )
            cons_sess.add(arstap2upstap)
    return


def handle_documenten(worksheet):
    """
    This procedure will handle the worksheet 'Document' to link Archief Document with the codes from
    Uitwisselingsplatform.

    :param worksheet: Pointer to the Document worksheet.

    :return:
    """
    logging.info("Handling Documenten")
    # Convert worksheet info to list of rows.
    row_list = list(worksheet.rows)
    # Get name tuple from title row
    title_row = row_list.pop(0)
    nr = get_named_row('Document', title_row)
    documenten = {}
    for row in map(nr._make, row_list):
        if row.Koppeling.value:
            code = row.code.value
            protege_id = row.Koppeling.value
            try:
                ardocument_id = documenten[protege_id]
            except KeyError:
                ardocument = cons_sess.query(ArDocument).filter_by(protege_id=protege_id).one()
                documenten[protege_id] = ardocument.id
                ardocument_id = documenten[protege_id]
            try:
                source='dossierstuk'
                updocument = cons_sess.query(UpDocument).filter_by(code=code).filter_by(source=source).one()
            except NoResultFound:
                source='datablok'
                updocument = cons_sess.query(UpDocument).filter_by(code=code).filter_by(source=source).one()
            updocument_id = updocument.id
            ardocument2updocument = ArDocument2UpDocument(
                ardocument_id=ardocument_id,
                updocument_id=updocument_id
            )
            cons_sess.add(ardocument2updocument)
    cons_sess.commit()
    return


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
    handle_gebeurtenis(worksheet=wb['Gebeurtenis'])
    # Then work on Fases
    handle_fase(worksheet=wb['Fase'])
    # Then work on Dossiertype
    handle_dossiertype(worksheet=wb['Dossiertype'])
    # Work on Stappen: connect procedure stappen from Archief en Uitwisselingsplatform.
    handle_stappen(worksheet=wb['Stappen'])
    # Work on the Documenten
    handle_documenten(worksheet=wb['Document'])
    # Commit all data to the database.
    cons_sess.commit()
    logging.info('End Application')
