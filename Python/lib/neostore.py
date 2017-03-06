"""
This class consolidates functions related to the neo4J datastore.
"""

import logging
import sys
from pandas import DataFrame
from py2neo import Graph, Node, Relationship, NodeSelector
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
        self.selector = NodeSelector(self.graph)
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

    def calc_nodes(self, label):
        """
        This function will calculate the number of nodes for the label specified
        @param label: Calculate number of nodes for this label
        @return: Number of nodes
        """
        query = "MATCH (n:{label}) RETURN count(n) as cnt".format(label=label)
        df = DataFrame(self.graph.run(query).data())
        cnt_arr = next(df.iterrows())[1]
        cnt = cnt_arr['cnt']
        return cnt

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

    def denorm_aanleg_3(self):
        """
        Function to return denormalized table (Dossiertype, Aanleg, Procedurestap)
        Note that you need a distinct in the return class. This is not required in case a.naam and c.naam are
        replaced with a.label and c.label.
        Do not use - see comment in 4_neo_add_aanleg.py
        @return: denormalized table with columns aanleg, procedure, procedurestap
        """
        query = """
                match (a:Dossiertype)<-[:aanleg_bij_type]-(b:Aanleg)<-[:in_aanleg]-(c:ProcedureStap)
                return distinct b.naam as aanleg, a.naam as procedure, c.naam as procedurestap
                """
        dnt = DataFrame(self.graph.run(query).data())
        return dnt

    def denorm_aanleg_4(self):
        """
        Function to return denormalized table (Dossiertype, Aanleg, Procedurestap, Document)
        Do not use - see comment in 4_neo_add_aanleg.py
        @return: denormalized table with columns aanleg, procedure, procedurestap, document
        """
        query = """
                match (a:Dossiertype)<-[:aanleg_bij_type]-(b:Aanleg)<-[:in_aanleg]-(c:ProcedureStap)
                      <-[:bij_procedurestap]-(d:Document)
                return distinct b.naam as aanleg, a.naam as procedure, c.naam as procedurestap, d.naam as document
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
        @param left_node: FROM node
        @param rel:
        @param right_node: TO node
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

    def get_commentaar(self):
        """
        This function will collect the Commentaar and return it in a dictionary list.
        @return:
        """
        query = """
            MATCH (n)
            WHERE n.commentaar CONTAINS "???"
            RETURN labels(n) AS labels, n.naam AS naam, n.label AS label, n.commentaar AS commentaar
        """
        res = self.graph.run(query)
        return res.data()

    def get_aanleg4type(self, dossiertype_id):
        """
        This function will get the graph for the dossiertype - aanleg - procedurestap, but avoiding Cartesian Product.
        @param dossiertype_id: Protege ID for Dossiertype
        @return: Dictionary of Nodes with Aanleg. The nodes are the keys of the dictionary. Values are 1.
        """
        query = """
        MATCH (d:Dossiertype)<-[:voor_dossiertype]-(f:ProcedureFase)-[:aanleg]->(a:Aanleg)
        WHERE d.protege_id = '{id}'
        RETURN a
        ORDER BY a.naam
        """.format(id=dossiertype_id)
        res = self.graph.run(query)
        # Be careful, Cursor will return duplicate nodes!
        # Get the list of unique nodes
        node_list = {}
        while res.forward():
            current = res.current()
            (node, ) = current.values()
            node_list[node] = 1
        return node_list

    def get_stap(self, dossiertype_id, aanleg):
        """
        This function will get the graph for the dossiertype - aanleg - procedurestap, but avoiding Cartesian Product.
        @param dossiertype_id: Protege ID for Dossiertype
        @param aanleg: Naam of the Aanleg
        @return: Dictionary of Nodes with Aanleg. The nodes are the keys of the dictionary. Values are 1.
        """
        query = """
        MATCH (d:Dossiertype)<-[:voor_dossiertype]-(f:ProcedureFase)<-[:in_procedure]-(s:ProcedureStap),
              (f)-[:aanleg]->(a:Aanleg)
        WHERE d.protege_id = '{id}'
          AND a.naam = '{a}'
        RETURN s
        ORDER BY s.naam
        """.format(id=dossiertype_id, a=aanleg)
        res = self.graph.run(query)
        # Be careful, Cursor will return duplicate nodes!
        # Get the list of unique nodes
        node_list = {}
        while res.forward():
            current = res.current()
            (node, ) = current.values()
            node_list[node] = 1
        return node_list

    def get_reference(self, prot_id):
        """
        This function will get the references (artikels) for the different topics.
        @param prot_id: Protege ID of the Procedure - document node for which references are searched.
        @return: False - if no references, or formatted string of references.
        """
        query = """
        match (a)-[:in_artikel]->(b:Artikel)-[:artikel_in_toc]->(c),
        (a)-[:beschreven_in]->(c),
        (b)-[:artikel_in_boek]->(d:Boek)
        where a.protege_id = '{}'
        return a.naam, b.artikel as artikel, c.toc as toc, c.item as item, d.item as boek
        order by boek, artikel
        """.format(prot_id)
        refs = DataFrame(self.graph.run(query).data())
        # No references for this item, return False
        if refs.empty:
            return False
        # References defined, return them
        refline = ""
        for refrow in refs.iterrows():
            boek = refrow[1]['boek']
            item = refrow[1]['item']
            toc = refrow[1]['toc']
            artikel = refrow[1]['artikel']
            refline = "{r}* {b} - {t} {i}, Artikel {a}\n".format(r=refline, b=boek, i=item, t=toc, a=artikel)
        if len(refline) > 5:
            # Add another CRLF
            refline = "{}\n".format(refline)
        return refline

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

    def get_aanleg_paths(self, aanleg):
        """
        This function gets aanleg string (Eerste Aanleg, Laatste Aanleg) and finds all paths Dossiertype -
        ProcedureFase - ProcedureStap for this aanleg.
        The function will return the Dossiertype nodes and the ProcedureStap nodes.
        @param aanleg:
        @return: Cursor with Node Dossiertype, ProcedureFase and ProcedureStap
        """
        query = """
        MATCH (d:Dossiertype)<-[:voor_dossiertype]-(f:ProcedureFase),
              (f)<-[:in_procedure]-(s:ProcedureStap)
        WHERE f.naam contains '{aanleg}'
        RETURN d,f,s
        """.format(aanleg=aanleg)
        res = self.graph.run(query)
        return res

    def get_no_aanleg_paths(self):
        """
        This function finds all paths Dossiertype - ProcedureFase - ProcedureStap for which naam ProcedureFase does
        not contain 'Aanleg'.
        The function will return the Nodes Dossiertype, ProcedureFase and ProcedureStap.
        @return: Cursor with Nodes Dossiertype, ProcedureFase and ProcedureStap
        """
        query = """
        MATCH (d:Dossiertype)<-[:voor_dossiertype]-(f:ProcedureFase),
              (f)<-[:in_procedure]-(s:ProcedureStap)
        WHERE not (f.naam contains 'Aanleg')
        RETURN d,f,s
        """
        res = self.graph.run(query)
        return res

    def get_relations_togroup(self, from_label, to_label, rel_type, to_nodes):
        """
        This function will return the naam and the protege_id for all nodes from label from_label to label to_label
        if the target (to) nodes are in the group to_nodes. The relation type is rel_type.
        @param from_label: Label for the FROM node
        @param to_label: Label for the TO node
        @param rel_type: Relation Type
        @param to_nodes: List of ending nodes that are in scope.
        @return: from_name, from_id, to_name, to_id
        """
        query = """
                match (f:{from_label})-[:{rel_type}]->(t:{to_label})
                where t.protege_id in {to_nodes}
                return f.naam as f_naam, f.protege_id as f_id,
                t.naam as t_naam, t.protege_id as t_id
                """.format(from_label=from_label, to_label=to_label, rel_type=rel_type, to_nodes=to_nodes)
        return DataFrame(self.graph.run(query).data())

    def get_nodes_from_orphan(self, from_label, rel_type):
        """
        This function will return the naam and the label for all nodes for which a mandatory FROM relation is
        missing.
        @param from_label: Label for the FROM node
        @param rel_type: Relation Type
        @return: Pandas Dataframe with from_name, from_label
        """
        query = """
                match (f:{from_label})
                where not (f)-[:{rel_type}]->()
                return f.naam as naam, f.label as label
                """.format(from_label=from_label, rel_type=rel_type)
        return DataFrame(self.graph.run(query).data())

    def get_nodes_to_orphan(self, to_label, rel_type):
        """
        This function will return the naam and the label for all nodes for which a mandatory TO relation is
        missing.
        @param to_label: Label for the TO node
        @param rel_type: Relation Type
        @return: Pandas Dataframe with to_name, to_label
        """
        query = """
                match (t:{to_label})
                where not (t)<-[:{rel_type}]-()
                return t.naam as naam, t.label as label
                """.format(to_label=to_label, rel_type=rel_type)
        return DataFrame(self.graph.run(query).data())

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
        @param end_node: End node of the relation
        @param rel_type:Start node of the relation
        @return: array of relations (start_node, rel_type, end_node)
        """
        rel_array = []
        for rel in self.graph.match(rel_type=rel_type, end_node=end_node):
            rel_array.append(rel)
        return rel_array

    def del_relation(self, from_node, rel_type, to_node):
        """
        This function will remove the relation between from_node and to_node
        @param from_node: the from_node
        @param rel_type: Relation type to remove
        @param to_node: the to_node in the relation
        @return:
        """
        nid = "protege_id"
        from_node_id = from_node[nid]
        to_node_id = to_node[nid]
        query = """
                MATCH (f)-[r:{rel}]->(t)
                WHERE f.{nid} = '{f_nid}'
                  AND t.{nid} = '{t_nid}'
                DELETE r
                """.format(rel=rel_type, nid=nid, f_nid=from_node_id, t_nid=to_node_id)
        self.graph.run(query)
        return
