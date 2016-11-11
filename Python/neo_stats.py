"""
This procedure will get statistics and will do some error checking.
"""

import logging
from lib import my_env
from lib import neostore


if __name__ == "__main__":
    # Initialize Environment
    cfg = my_env.init_env("convert_protege", __file__)
    # Get NeoStore object
    ns = neostore.NeoStore(cfg)
    labels = ['Dossiertype', 'ProcedureFase', 'ProcedureStap', 'Document',
              'Artikel', 'Boek', 'Titel', 'Hoofdstuk', 'Afdeling', 'Onderafdeling']
    logging.info("Before FOR")
    for label in labels:
        logging.info("{label}: {cnt}".format(label=label, cnt=ns.calc_nodes(label)))
    logging.info("After FOR")
