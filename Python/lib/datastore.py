"""
This class consolidates functions related to the local mysql datastore.
"""

import logging
import sqlite3


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
        db_conn = sqlite3.connect(db)
        logging.debug("Datastore object and cursor are created")
        db_conn.row_factory = sqlite3.Row
        return db_conn, db_conn.cursor()

    def close_connection(self):
        """
        Method to close the Database Connection.
        :return:
        """
        logging.debug("Close connection to database")
        self.dbConn.close()
        return

    def create_tables(self):
        self.create_table_components()
        self.create_table_relations()
        return

    def clear_tables(self):
        for table in self.tables:
            query = "DELETE FROM {table}".format(table=table)
            self.dbConn.execute(query)
            logging.info("Clear table {table}".format(table=table))

    def remove_tables(self):
        for table in self.tables:
            self.remove_table(table)

    def remove_table(self, table):
        query = "DROP TABLE IF EXISTS {table}".format(table=table)
        self.dbConn.execute(query)
        logging.info("Drop table {table}".format(table=table))
        return True

    def create_table_components(self):
        # Create table
        # Get the field names from Protege - Slots, where Value Type is not Instance.
        # class and protege_id are fixed and should always be there.
        query = """
        CREATE TABLE components
            (id integer primary key autoincrement,
             naam text,
             class text,
             protege_id text unique,
             commentaar text,
             afdeling text,
             artikel text,
             bladzijde text,
             hoofdstuk text,
             onderafdeling text,
             titel text,
             titel_item text,
             url text,
             in_bereik text)
        """
        self.dbConn.execute(query)
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
        self.dbConn.execute(query)
        logging.info("Table relations is build.")
        return True

    def remove_table_user_data(self):
        query = 'DROP TABLE IF EXISTS user_data'
        self.dbConn.execute(query)
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
        self.dbConn.execute(query, values)
        self.dbConn.commit()
        return

    def go_down(self, item):
        """
        This method will get an item (Protege ID) and find all items further down the hierarchy. So item is
        target. Return will be list of tuples (source, relation type, naam). But it can be accessed using dictionary
        since row_factory has been set to the cursor.
        @param item: ProtegeID of the start item.
        @return: list of tuples (source item, relation type, naam).
        """
        # SELECT source, rel_type, naam
        query = """
                SELECT *
                FROM relations
                JOIN components ON source=protege_id
                WHERE target=?
                AND rel_type not like '%gebeurtenis%'
                AND NOT rel_type = 'in_procedurestap'
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
        # SELECT target, rel_type, naam
        query = """
                SELECT *
                FROM relations
                JOIN components ON target=protege_id
                WHERE source=?
                AND rel_type not like '%gebeurtenis%'
                AND NOT rel_type = 'in_procedurestap'
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

    def get_components(self):
        """
        This method will return all components with all attributes from the components table 'in_bereik'.
        @return: Array of components. Each component is a dictionary of the array.
        """
        query = "SELECT * FROM components"
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    def get_relations(self):
        """
        This method will return all relations from the relations table.
        @return: Array of relations. Each relation is a dictionary of the array.
        """
        query = "SELECT * FROM relations"
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    def get_components_type(self, comp_type='Dossiertype'):
        """
        This method will return all components of a specific type (class).
        @param comp_type: Class (type) for which list of components is required. Default: 'Dossiertype'.
        @return: List of Protege IDs of the components.
        """
        query = "SELECT protege_id FROM components WHERE class = ?"
        self.cur.execute(query, (comp_type,))
        rows = self.cur.fetchall()
        return [dt['protege_id'] for dt in rows]
