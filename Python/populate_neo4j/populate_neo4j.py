"""
This script will convert protege data and load it into Neo4J.
This is done calling applications in sequence.
"""
# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

import logging
from lib import my_env
from lib.my_env import run_script

if __name__ == "__main__":

    (fp, filename) = os.path.split(__file__)

    logging.info("Convert Protege RDF files into SQLite tables")
    run_script(fp, '1_rdf2sql.py')

    logging.info("Import SQLite tables into Neo4J")
    run_script(fp, '2_sql2neo.py')

    logging.info("Duplicate Openbaar Onderzoek for Bijstelling Voorwerp/Duur Omgevingsvergunning")
    run_script(fp, '3_voorwerpduur_oo.py')

    logging.info("Add Aanleg Nodes into Neo4J")
    run_script(fp, '4_neo_add_aanleg.py')

    logging.info("Test Neo4J content")
    run_script(fp, 'neo_stats.py')
