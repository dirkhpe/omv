"""
This script will convert a table of contents document and load it into Neo4J. The table of contents document can have
the structure Titel - Hoofdstuk - Afdeling - Onderafdeling. Each line in table of contents file has it's number and
category. The sequence of table of contents file determines the table. This means that parents are above children.
The assumption is that categories are in correct sequence.
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
    # Configure Command line argumentsb
    parser = argparse.ArgumentParser(
            description="Script to read table of contents worksheet info and convert it into a graph."
    )
    parser.add_argument('-s', '--sheet', default='Uitvoeringsbesluit',
                        help='Worksheet name. Default is "Uitvoeringsbesluit".',
                        choices=['Uitvoeringsbesluit', 'Decreet'])
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
    # First remove all nodes and relations for this label
    ns.remove_nodes(args.sheet)
    # Add Book node
    valuedict = {
        'item': args.sheet,
        'label': args.sheet
    }
    node_label = 'book'
    node = ns.create_node(node_label, args.sheet, **valuedict)
    node_obj[0] = node
    # I need to initialize toc_titel, because it is not sure I'll have a title.
    toc_titel = "."
    toc_hoofdstuk = ""
    toc_afdeling = ""
    toc_onderafdeling = ""
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
        nid = row.ID.value
        msg = "ID: {nid} - deel: {deel} - nr: {nr} - label: {lbl}".format(nid=nid, deel=row.Deel.value,
                                                                          nr=row.Nr.value, lbl=row.Label.value)
        logging.warning(msg)
        if deel == 'Onderafdeling':
            # link to afdeling
            lnid = nid_afdeling
            # Set toc
            toc_onderafdeling = "{t}{n}.".format(t=toc_afdeling, n=row.Nr.value)
            valuedict['toc'] = toc_onderafdeling
        elif deel == 'Afdeling':
            # Link to Hoofdstuk
            lnid = nid_hoofdstuk
            # Remember afdeling
            nid_afdeling = nid
            # Set toc
            toc_afdeling = "{t}{n}.".format(t=toc_hoofdstuk, n=row.Nr.value)
            valuedict['toc'] = toc_afdeling
        elif deel == 'Hoofdstuk':
            # Link to Titel
            lnid = nid_titel
            # Remember hoofdstuk
            nid_hoofdstuk = nid
            # Set toc
            toc_hoofdstuk = "{t}{n}.".format(t=toc_titel, n=row.Nr.value)
            valuedict['toc'] = toc_hoofdstuk
        elif deel == 'Titel':
            # Link to Book
            lnid = 0
            # Remember titel
            nid_titel = nid
            # Set toc
            toc_titel = "{}.".format(row.Nr.value)
            valuedict['toc'] = toc_titel
        elif not deel:
            break
        else:
            logging.error("Unknown 'deel' found: {d} for item {i}".format(d=row.Deel.value, i=row.Item.value))
            lnid = 0
        # Create node
        node = ns.create_node(deel, args.sheet, **valuedict)
        # Remember node
        node_obj[nid] = node
        # Create relation to parent.
        rel = ns.create_relation(node_obj[lnid], 'heeft_deel', node)
        logging.warning("Parent: {lnid} - Child: {nid}".format(lnid=lnid, nid=nid))
