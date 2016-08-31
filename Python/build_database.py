"""
This script will rebuild the database from scratch. It should run only once during production
and many times during development.
"""

import logging
from lib.datastore import DataStore
from lib import my_env


def main():
    cfg = my_env.init_env("convert_protege", __file__)
    ds = DataStore(cfg)
    ds.remove_tables()
    ds.create_tables()
    logging.info('End Application')


if __name__ == "__main__":
    main()
