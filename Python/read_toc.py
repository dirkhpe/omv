"""
This script will read Worksheet name and collect table of contents from it.
"""

import argparse
import logging
from collections import namedtuple
from lib import my_env
from lib import neostore
from openpyxl import load_workbook


def get_named_row(col_hrd):
    """
    This method will create a named tuple row.
    @param col_hrd: Where the column information is stored.
    :return: namedtuple class with name "named_row"
    """
    # Get column names
    field_list = [cell.value for cell in col_hrd]
    # Create named tuple subclass with name "named_row"
    named_row = namedtuple("my_named_row", field_list, rename=True)
    return named_row


if __name__ == "__main__":
    # Configure Command line arguments
    parser = argparse.ArgumentParser(
            description="Script to read table of contents worksheet info and convert it into a graph."
    )
    parser.add_argument('-s', '--sheet', default='Decreet 25.04.14',
                        help='Worksheet name. Default is "Decreet 25.04.14".',
                        choices=['Decreet 25.04.14', '(to be completed)'])
    args = parser.parse_args()
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    ns = neostore.NeoStore(cfg)
    # Initialize graph / node values
    node_obj = {}
    nid_titel = 0
    nid_hoofdstuk = 0
    nid_afdeling = 0
    # Get Workbook information
    wb = load_workbook(cfg['Main']['tocbook'], read_only=True)
    ws = wb[args.sheet]
    # Convert worksheet info to list of rows.
    row_list = list(ws.rows)
    # Get name tuple from title row
    title_row = row_list.pop(0)
    nr = get_named_row(title_row)
    # Add Book node
    valuedict = {
        'item': args.sheet,
        'label': args.sheet
    }
    node_label = 'book'
    node = ns.create_node(node_label, args.sheet, **valuedict)
    node_obj[0] = node
    # I can convert all remaining rows in 1 go now, but still need to access .value.
    for row in map(nr._make, row_list):
        deel = row.Deel.value
        valuedict = {
            'deel': row.Deel.value,
            'nr': row.Nr.value,
            'item': row.Item.value,
            'pagina': row.Pagina.value,
            'label': row.Label.value,
        }
        # Create node
        node = ns.create_node(deel, args.sheet, **valuedict)
        nid = row.ID.value
        node_obj[nid] = node
        if deel == 'Onderafdeling':
            # link to afdeling
            lnid = nid_afdeling
        elif deel == 'Afdeling':
            # Link to Hoofdstuk
            lnid = nid_hoofdstuk
            # Remember afdeling
            nid_afdeling = nid
        elif deel == 'Hoofdstuk':
            # Link to Titel
            lnid = nid_titel
            # Remember hoofdstuk
            nid_hoofdstuk = nid
        elif deel == 'Titel':
            # Link to Book
            lnid = 0
            # Remember titel
            nid_titel = nid
        else:
            logging.error("Unknown 'deel' found: {d} for item {i}".format(d=row.Deel.value, i=row.Item.value))
            lnid = 0
        rel = ns.create_relation(node_obj[lnid], 'heeft_deel', node)
