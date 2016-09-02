"""
This class consolidates functions related to the local datastore.
"""

import logging
import sqlite3
import sys


class DataStore:

    tables = ['components', 'relations']

    def __init__(self, config):
        """
        Method to instantiate the class in an object for the datastore.
        :param config object, to get connection parameters.
        :return: Object to handle datastore commands.
        """
        logging.debug("Initializing Datastore object")
        self.config = config
        self.dbConn, self.cur = self._connect2db()
        return

    def _connect2db(self):
        """
        Internal method to create a database connection and a cursor. This method is called during object
        initialization.
        Note that sqlite connection object does not test the Database connection. If database does not exist, this
        method will not fail. This is expected behaviour, since it will be called to create databases as well.
        :return: Database handle and cursor for the database.
        """
        logging.debug("Creating Datastore object and cursor")
        db = self.config['Main']['db']
        try:
            db_conn = sqlite3.connect(db)
        except:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            log_msg = "Error during connect to database: %s %s"
            logging.error(log_msg, e, ec)
            return
        else:
            logging.debug("Datastore object and cursor are created")
            # Now throw in Row factory so that we can use key/value based records
            # fetchone, fetchall will return tuples that can be accessed on key.
            db_conn.row_factory = sqlite3.Row
            return db_conn, db_conn.cursor()

    def close_connection(self):
        """
        Method to close the Database Connection.
        :return:
        """
        logging.debug("Close connection to database")
        try:
            self.dbConn.close()
        except:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            log_msg = "Error during close connect to database: %s %s"
            logging.error(log_msg, e, ec)
            return
        else:
            return

    def create_tables(self):
        self.create_table_components()
        self.create_table_relations()
        return

    def clear_tables(self):
        for table in self.tables:
            query = "DELETE FROM {table}".format(table=table)
            try:
                self.dbConn.execute(query)
            except:
                e = sys.exc_info()[1]
                ec = sys.exc_info()[0]
                log_msg = "Error during query execution: %s %s"
                logging.error(log_msg, e, ec)
                return False
            else:
                logging.info("Clear table {table}".format(table=table))

    def remove_tables(self):
        for table in self.tables:
            self.remove_table(table)

    def remove_table(self, table):
        query = "DROP TABLE IF EXISTS {table}".format(table=table)
        try:
            self.dbConn.execute(query)
        except:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            log_msg = "Error during query execution: %s %s"
            logging.error(log_msg, e, ec)
            return False
        else:
            logging.info("Drop table {table}".format(table=table))
            return True

    def create_table_components(self):
        # Create table
        query = """
        CREATE TABLE components
            (id integer primary key autoincrement,
             naam text,
             class text,
             protege_id text unique,
             beschrijving text,
             formaat text,
             identifier text,
             in_bereik text)
        """
        try:
            self.dbConn.execute(query)
        except:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            log_msg = "Error during query execution - Attribute_action: %s %s"
            logging.error(log_msg, e, ec)
            return False
        logging.info("Table components is build.")
        return True

    def create_table_relations(self):
        # Create table
        query = """
        CREATE TABLE relations
            (id integer primary key autoincrement,
             rel_type text,
             source text,
             target text)
        """
        try:
            self.dbConn.execute(query)
        except:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            log_msg = "Error during query execution - Attribute_action: %s %s"
            logging.error(log_msg, e, ec)
            return False
        logging.info("Table relations is build.")
        return True

    def remove_table_user_data(self):
        query = 'DROP TABLE IF EXISTS user_data'
        try:
            self.dbConn.execute(query)
        except:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            log_msg = "Error during query execution: %s %s"
            logging.error(log_msg, e, ec)
            return False
        else:
            logging.info("Drop table user_data")
            return True

    def get_columns(self, tablename):
        """
        This method will get column names for the specified table.
        :param tablename:
        :return:
        """
        cols = self.cur.execute("PRAGMA table_info({tn})".format(tn=tablename))
        return [col[1] for col in cols]

    def insert_row(self, tablename, rowdict):
        columns = ", ".join(rowdict.keys())
        values_template = ", ".join(["?"] * len(rowdict.keys()))
        query = "insert into  {tn} ({cols}) values ({vt})".format(tn=tablename, cols=columns, vt=values_template)
        values = tuple(rowdict[key] for key in rowdict.keys())
        try:
            self.dbConn.execute(query, values)
        except:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            log_msg = "Error during query execution: %s %s"
            logging.error(log_msg, e, ec)
            return False
        try:
            self.dbConn.commit()
        except:
            e = sys.exc_info()[1]
            ec = sys.exc_info()[0]
            log_msg = "Error during query execution: %s %s"
            logging.error(log_msg, e, ec)
            return False
        return

    def go_down(self, item):
        """
        This method will get an item (Protege ID) and find all items further down the hierarchy. So item is
        target. Return will be list of tuples (source, relation type, naam). But it can be accessed using dictionary
        since row_factory has been set to the cursor.
        @param item: ProtegeID of the start item.
        @return: list of tuples (source item, relation type, naam).
        """
        query = """
                SELECT source, rel_type, naam
                FROM relations
                JOIN components ON source=protege_id
                WHERE target=?
                """
        # logging.debug("{q} - {i}".format(q=query, i=item))
        self.cur.execute(query, (item,))
        res = self.cur.fetchall()
        return res

    def go_up(self, item):
        """
        This method will get an item (Protege ID) and find all items further up the hierarchy. So item is
        source. Return will be list of tuples (source, relation type, naam). But it can be accessed using dictionary
        since row_factory has been set to the cursor.
        @param item: ProtegeID of the start item.
        @return: list of tuples (target item, relation type, naam).
        """
        query = """
                SELECT target, rel_type, naam
                FROM relations
                JOIN components ON target=protege_id
                WHERE source=?
                """
        # logging.debug("{q} - {i}".format(q=query, i=item))
        self.cur.execute(query, (item,))
        res = self.cur.fetchall()
        return res

    def get_comp_attribs(self, item):
        """
        This method will read the component table for the item.
        @param item: Protege ID of the item to search for.
        @return: Single sequence of attributes, or none.
        """
        query = "SELECT * FROM components WHERE protege_id=?"
        self.cur.execute(query, (item,))
        res = self.cur.fetchone()
        return res
