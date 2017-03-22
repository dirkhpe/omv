"""
This module implements a class to create Excel Workbooks.
"""

from copy import copy
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.styles.borders import Border, Side


class Write2Excel:
    """
    This class consolidates the functions to write the data to excel workbook a nice format.
    """

    def __init__(self):
        """
        Create the workbook object and set the initial sheet.
        """
        self.wb = Workbook()
        self.current_sheet = self.wb.active

    def init_sheet(self, title):
        """
        Initialize the worksheet.

        :param title: mandatory title for the worksheet

        :return: worksheet object
        """
        if self.current_sheet.title == 'Sheet':
            # This is the initial sheet, re-assign title
            self.current_sheet.title = title
        else:
            # There are sheets already, finalize the sheet and create a new one
            finalize_sheet(self.current_sheet)
            self.current_sheet = self.wb.create_sheet(title=title)
        initialize_sheet(self.current_sheet)
        return self.current_sheet

    def close_workbook(self, filename):
        """
        This method will finalize the current sheet and close the file.
        :param filename:
        :return:
        """
        finalize_sheet(self.current_sheet)
        self.wb.save(filename=filename)
        return


def initialize_sheet(ws):

    # ws1.auto_filter.ref = "A2:F100"

    # Set column width
    ws.column_dimensions[get_column_letter(1)].width = 10
    ws.column_dimensions[get_column_letter(2)].width = 10
    ws.column_dimensions[get_column_letter(3)].width = 32
    ws.column_dimensions[get_column_letter(4)].width = 72
    ws.column_dimensions[get_column_letter(5)].width = 72
    ws.column_dimensions[get_column_letter(6)].width = 32

    # Set row height
    ws.row_dimensions[1].height = 24
    ws.row_dimensions[2].height = 24

    # Create Title Row 1
    bg_color = 'BFBFBF'
    fill_r1 = PatternFill(start_color=bg_color, end_color=bg_color, fill_type='solid')
    ws.merge_cells('A1:B1')
    ws.merge_cells('C1:D1')
    ws.merge_cells('E1:F1')
    ws['A1'] = 'Wetgeving Artikels'
    ws['C1'] = 'Register'
    ws['E1'] = 'Omgevingsloket'
    ws['A1'].fill = fill_r1
    ws['C1'].fill = fill_r1
    ws['E1'].fill = fill_r1
    set_bold(ws['A1'])
    set_bold(ws['C1'])
    set_bold(ws['E1'])
    ws['A1'].alignment = Alignment(horizontal='center')
    ws['C1'].alignment = Alignment(horizontal='center')
    ws['E1'].alignment = Alignment(horizontal='center')

    # Create Title Row 2
    bg_color = 'D9D9D9'
    fill_r2 = PatternFill(start_color=bg_color, end_color=bg_color, fill_type='solid')
    title_row = ['decreet', 'besluit', 'stap', 'document - archief', 'document -loket', 'gebeurtenis']
    row = 2
    for pos in range(len(title_row)):
        col = pos + 1
        ws[rc2a1(row, col)] = title_row[pos]
        ws[rc2a1(row, col)].fill = fill_r2
        set_bold(ws[rc2a1(row, col)])


def finalize_sheet(ws):
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    for row in ws['A1:F100']:
        for cell in row:
            cell.border = thin_border


def rc2a1(row=None, col=None):
    """
    This function converts a (row, column) pair (R1C1 notation) to the A1 string notation for excel. The column number
    is converted to the character(s), the row number is appended to the column string.

    :param col: Row number (1 .. )

    :param row: Column number (1 .. )

    :return: A1 Notation (e.g. 'BF19745')
    """
    return "{0}{1}".format(get_column_letter(col), row)


def set_bold(cell):
    """
    This function will set the font of the cell to bold. In openpyxl cell styles are shared between objects and once
    assigned they cannot be changed anymore. This stops unwanted side-effects such as changing lots of cells instead of
    one single cell.

    :param cell: Font for this cell needs to be set to bold.
    :return: Nothing, but the font of the cell has been changed to bold in the mean time.
    """
    this_font = cell.font
    that_font = copy(this_font)
    that_font.bold = True
    cell.font = that_font
    return
