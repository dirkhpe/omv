"""
This class consolidates functions related to the neo4J datastore.
"""

import logging
import sys
from pandas import DataFrame
from py2neo import Graph, Node, Relationship
from py2neo.database import DBMS


class NeoStore:

    def __init__(self, config):
        """
        Method to instantiate the class in an object for the neostore.
        :param config object, to get connection parameters.
        :return: Object to handle neostore commands.
        """
        logging.debug("Initializing Neostore object")
        self.config = config
        self.graph = self._connect2db()
        return

    def _connect2db(self):
        """
        Internal method to create a database connection. This method is called during object initialization.
        :return: Database handle and cursor for the database.
        """
        logging.debug("Creating Neostore object.")
        neo4j_config = {
            'user': self.config['Graph']['username'],
            'password': self.config['Graph']['password'],
        }
        # Connect to Graph
        graph = Graph(**neo4j_config)
        # Check that we are connected to the expected Neo4J Store - to avoid accidents...
        dbname = DBMS().database_name
        if dbname != self.config['Main']['neo_db']:
            logging.fatal("Connected to Neo4J database {d}, but expected to be connected to {n}"
                          .format(d=dbname, n=self.config['Main']['neo_db']))
            sys.exit(1)
        return graph

    def denorm_table_3(self):
        """
        Function to return denormalized table (Dossiertype, ProcedureFase, Procedurestap)
        @return: denormalized table with columns aanleg, procedure, procedurestap
        """
        query = """
                match (a:Dossiertype)<-[:voor_dossiertype]-(b:ProcedureFase)<-[:in_procedure]-(c:ProcedureStap)
                return b.naam as aanleg, a.naam as procedure, c.naam as procedurestap
                """
        dnt = DataFrame(self.graph.run(query).data())
        return dnt

    def denorm_table_4(self):
        """
        Function to return denormalized table (Dossiertype, ProcedureFase, Procedurestap, Document)
        @return: denormalized table with columns aanleg, procedure, procedurestap, document
        """
        query = """
                match (a:Dossiertype)<-[:voor_dossiertype]-(b:ProcedureFase)<-[:in_procedure]-(c:ProcedureStap)
                      <-[:bij_procedurestap]-(d:Document)
                return b.naam as aanleg, a.naam as procedure, c.naam as procedurestap, d.naam as document
                """
        dnt = DataFrame(self.graph.run(query).data())
        return dnt

    def create_node(self, *labels, **props):
        """
        Function to create node. The function will return the node object.
        @param labels: Labels for the node
        @param props: Value dictionary with values for the node.
        @return:
        """
        component = Node(*labels, **props)
        self.graph.create(component)
        return component

    def create_relation(self, left_node, rel, right_node):
        """
        Function to create relationship between nodes.
        @param left_node:
        @param rel:
        @param right_node:
        @return:
        """
        rel = Relationship(left_node, rel, right_node)
        self.graph.merge(rel)
        return

    def get_components_book(self, left, blabel=None):
        """
        This function will get all relations between types left and right for book with label blabel.
        @param left: Type of the left node
        @param blabel: Type of the right node. Relation between left and right is 'heeft_deel'.
        @return:
        """
        query = """
                MATCH (l:{l})-[:heeft_deel]->(r)
                WHERE '{bl}' in labels(l)
                RETURN l.label as llabel, r.label as rlabel, id(l) as lid, id(r) as rid, r.nr as rnr, r.pagina as pagina
                ORDER BY l.nr, r.nr
                """.format(l=left, bl=blabel)
        dnt = DataFrame(self.graph.run(query).data())
        return dnt

    def get_topics(self, left_id):
        """
        This function will get all relations between node with ID left and right for book with label blabel.
        @param left_id: ID of the left node
        @return:
        """
        query = """
                MATCH (l)-[:heeft_deel]->(r)
                WHERE id(l)={left_id}
                RETURN l.label as llabel, r.label as rlabel, id(l) as lid, id(r) as rid, r.nr as rnr,
                       r.pagina as pagina
                ORDER BY l.nr, r.nr
                """.format(left_id=left_id)
        logging.debug(query)
        dnt = DataFrame(self.graph.run(query).data())
        return dnt

    def remove_nodes(self, label):
        """
        This function will remove all nodes and relations for a specific label.
        @param label: The label for which all nodes and relations will be removed.
        @return:
        """
        query = "MATCH (n) WHERE  '{l}' IN labels(n) DETACH DELETE n".format(l=label)
        logging.info("Query: {q}".format(q=query))
        self.graph.run(query)
        return

    def get_node(self, *labels, **kwargs):
        """
        This function will return a single node by label and optional properties.
        @param labels:
        @param kwargs:
        @return:
        """
        return self.graph.find_one(*labels, **kwargs)

    def get_nodes(self, *labels, **kwargs):
        """
        This function will return all nodes by label and optional properties.
        @param labels:
        @param kwargs:
        @return:
        """
        return self.graph.find(*labels, **kwargs)

    def get_start_nodes(self, end_node, rel_type):
        """
        This function will get all start nodes for relation rel_type and end node end_node
        @param end_node:
        @param rel_type:
        @return: array of relations (start_node, rel_type, end_node)
        """
        rel_array = []
        for rel in self.graph.match(rel_type=rel_type, end_node=end_node):
            rel_array.append(rel)
        return rel_array
