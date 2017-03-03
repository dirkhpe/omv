"""
This module consolidates the communication with Postgres database Omgevingsvergunning.
This is not done using sqlalchemy and reflection, since the schema is not default (public) but dedicated schema
omv. Also the Postgres database is using many specific features that are not understood by sqlalchemy.
Table queries are done using 'direct' SQL commands.
"""
import psycopg2
from collections import namedtuple


class Datastore:

    def __init__(self, config):
        """
        Datastore initialization. Connect to the database and create a cursor.
        :param config: Ini file object.
        :return:
        """
        # Get Postgres Connection string
        user = config['Postgres']['user']
        pwd = config['Postgres']['pwd']
        host = config['Postgres']['host']
        database = config['Postgres']['database']
        port = config['Postgres']['port']
        conn_string = "dbname={d} user={u} password={pwd} host={h} port={p}".format(
            d=database,
            u=user,
            pwd=pwd,
            h=host,
            p=port
        )
        self.cnx = psycopg2.connect(conn_string)
        self.cursor = self.cnx.cursor()

    def get_named_row(self, tablename):
        """
        This method will create a named tuple row for the current cursor.
        :return: namedtuple class with name "named_row"
        """
        # Get column names
        field_list = [x[0] for x in self.cursor.description]
        # Create named tuple subclass with name "named_row"
        named_row = namedtuple(tablename, field_list, rename=True)
        return named_row

    def get_table(self, tablename):
        """
        This method will return the table as a list of named rows. This means that each row in the list will return
        the table column value as an attribute. E.g. row.name will return the value for column name in each row.
        Schema name 'omv' will be appended to the table name.
        @param tablename:
        @return:
        """
        query = "SELECT * FROM omv.{t}".format(t=tablename)
        self.cursor.execute(query)
        named_row = self.get_named_row(tablename)
        rec_list = [row for row in map(named_row._make, self.cursor.fetchall())]
        return rec_list
