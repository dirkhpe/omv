"""
This file will extract the structure of the OMER Access database.
It should be sufficient generic to dump the structure of any Access Database.
The result is a file with Table names and Field names per table.
On Windows 7, install MS Access 64 bit driver from https://www.microsoft.com/en-us/download/details.aspx?id=13255
Check documentation from pyodbc module. Use the cursor.tables() and cursor.columns() methods.
"""

import argparse
import logging
import os
import pypyodbc
import sys
from lib import my_env


def connect_db(db_path):
    conn_str = 'driver=Microsoft Access Driver (*.mdb, *.accdb);dbq=' + db_path
    logging.debug("Connection String: %s", conn_str)
    try:
        db_conn = pypyodbc.connect(conn_str)
    except:
        e = sys.exc_info()[1]
        ec = sys.exc_info()[0]
        logmsg = "Error Class: %s, Message: %s"
        logging.critical(logmsg, ec, e)
        sys.exit()
    logmsg = "Connection Successful"
    logging.debug(logmsg)
    db_cur = db_conn.cursor()
    return db_conn, db_cur

if __name__ == "__main__":
    # Configure Command line arguments
    parser = argparse.ArgumentParser(
            description="Script to extract structure of an Access Database."
    )
    parser.add_argument('-d', '--db', default='c:\\temp\\omer.accdb',
                        help='Full path to the MS Access database.')
    args = parser.parse_args()
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    f = open(os.path.join(cfg['Main']['reportdir'], "{n}.csv".format(n="msaccess_struct")), mode='w')
    (conn, cur) = connect_db(args.db)
    tables = [row for row in cur.tables() if row["table_type"] == "TABLE"]
    f.write("Table,Column,Format,FK_Table,FK_Column\n")
    for t_row in tables:
        # Get list of FK in this table
        for c_row in cur.columns(table=t_row["table_name"]):
            f.write("{t},{c},{n}".format(t=t_row["table_name"], c=c_row["column_name"], n=c_row["type_name"]))
            f.write("\n")
    conn.close()
    f.close()
