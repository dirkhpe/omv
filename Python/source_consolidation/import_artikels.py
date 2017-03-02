"""
This script will convert a table of contents document and load it into SQL Database. The table of contents document can
have the structure Titel - Hoofdstuk - Afdeling - Onderafdeling. Each line in table of contents file has it's number and
category. The sequence of table of contents file determines the table. This means that parents are above children.
The assumption is that categories are in correct sequence.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import argparse
import logging
from collections import namedtuple
from lib import my_env
from lib import mysqlstore as mysql
from lib.mysqlstore import *
from openpyxl import load_workbook


def get_named_row(col_hrd):
    """
    This method will create a named tuple row.

    :param col_hrd: Where the column information is stored.

    :return: namedtuple class with name "named_row"
    """
    # Get column names
    field_list = [cell.value for cell in col_hrd]
    # Create named tuple subclass with name "named_row"
    named_row = namedtuple("my_named_row", field_list, rename=True)
    return named_row


if __name__ == "__main__":
    # Configure Command line argumentsb
    parser = argparse.ArgumentParser(
            description="Script to read table of contents worksheet info and convert it into a SQL Table."
    )
    parser.add_argument('-s', '--sheet', default='Uitvoeringsbesluit',
                        help='Worksheet name. Default is "Uitvoeringsbesluit".',
                        choices=['Uitvoeringsbesluit', 'Decreet'])
    args = parser.parse_args()
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"])
    # Get Workbook information
    wb = load_workbook(cfg['Main']['tocbook'], read_only=True)
    ws = wb[args.sheet]
    # Convert worksheet info to list of rows.
    row_list = list(ws.rows)
    # Get name tuple from title row
    title_row = row_list.pop(0)
    nr = get_named_row(title_row)
    # Add Book record
    boek = WetBoek(naam=args.sheet)
    cons_sess.add(boek)
    cons_sess.flush()
    # I need to initialize toc_titel, because it is not sure I'll have a title.
    toc_titel = None
    toc_hoofdstuk = None
    toc_afdeling = None
    toc_onderafdeling = None
    # I can convert all remaining rows in 1 go now, but still need to access .value.
    for row in map(nr._make, row_list):
        deel = row.Deel.value
        if deel == 'Onderafdeling':
            # Set toc
            toc_onderafdeling = row.Nr.value
        elif deel == 'Afdeling':
            toc_onderafdeling = None
            toc_afdeling = row.Nr.value
        elif deel == 'Hoofdstuk':
            toc_onderafdeling = None
            toc_afdeling = None
            toc_hoofdstuk = row.Nr.value
        elif deel == 'Titel':
            toc_onderafdeling = None
            toc_afdeling = None
            toc_hoofdstuk = None
            toc_titel = row.Nr.value
        elif not deel:
            break
        else:
            logging.error("Unknown 'deel' found: {d} for item {i}".format(d=row.Deel.value, i=row.Item.value))
        # Create toc record
        toc = WetToc(
            boek_id=boek.id,
            titel=toc_titel,
            hoofdstuk=toc_hoofdstuk,
            afdeling=toc_afdeling,
            onderafdeling=toc_onderafdeling,
            label=row.Label.value,
            item=row.Label.value
        )
        cons_sess.add(toc)
    cons_sess.commit()
    logging.info('End Application')
