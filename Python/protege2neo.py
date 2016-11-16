"""
This script will convert protege data and load it into Neo4J.
This is done calling applications in sequence.
"""

import logging
import os
import subprocess
from lib import my_env

if __name__ == "__main__":
    cfg = my_env.init_env('convert_protege', __file__)
    (filepath, filename) = os.path.split(__file__)
    python_path = os.path.join(filepath, 'omv', 'Scripts', 'python')
    # Convert Protege RDF files into SQLite tables
    script = os.path.join(filepath, '1_rdf2sql.py')
    logging.info("Convert Protege RDF files into SQLite tables")
    res = subprocess.call([python_path, script], env=os.environ.copy())
    # Import SQLite tables into Neo4J
    script = os.path.join(filepath, '2_sql2neo.py')
    logging.info("Import SQLite tables into Neo4J")
    res = subprocess.call([python_path, script], env=os.environ.copy())
    # Add Aanleg Nodes into Neo4J
    script = os.path.join(filepath, '3_neo_add_aanleg.py')
    logging.info("Add Aanleg Nodes into Neo4J")
    res = subprocess.call([python_path, script], env=os.environ.copy())
    # Test Neo4J content
    script = os.path.join(filepath, 'neo_stats.py')
    logging.info("Test Neo4J content")
    res = subprocess.call([python_path, script], env=os.environ.copy())
