"""
This class consolidates functions related to the neo4J datastore.
"""

import logging
from pandas import DataFrame
from py2neo import Graph, Node, Relationship


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
        try:
            graph = Graph(**neo4j_config)
        except:
            logging.exception("Connect to Neo4J failed: ")
            return
        else:
            return graph

    def denorm_table(self):
        """
        Function to return denormalized table (Dossiertype, Procedure, Procedurestap)
        @return: denormalized table
        """
        query = """
                MATCH (a:Dossiertype), (b:Procedure), (c:ProcedureStap)<-[r:bij_procedurestap]-(d:Document)
                RETURN a.naam as Dossiertype,b.naam as Procedure, c.naam as ProcedureStap, d.naam as Document
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
                RETURN l.label as llabel, r.label as rlabel, id(l) as lid, id(r) as rid, r.nr as rnr
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
                RETURN l.label as llabel, r.label as rlabel, id(l) as lid, id(r) as rid, r.nr as rnr
                ORDER BY l.nr, r.nr
                """.format(left_id=left_id)
        dnt = DataFrame(self.graph.run(query).data())
        return dnt
