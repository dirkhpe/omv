"""
This script will get the explorer-like graph for a book. It will get the book label and calculate the path down.
"""

import argparse
import logging
from lib import neostore
from lib import my_env


def delve_into(nid, dtoc):
    topics = ns.get_topics(nid)
    for topic in topics.iterrows():
        topic_id = topic[1]['rid']
        topic_toc = "{toc}{nr}.".format(toc=dtoc, nr=topic[1]['rnr'])
        logging.debug("{toc} {label}".format(toc=topic_toc, label=topic[1]['rlabel']))
        delve_into(topic_id, topic_toc)
    return


if __name__ == "__main__":
    # Configure Command line arguments
    parser = argparse.ArgumentParser(
            description="Script to create a explorer-like graph for book table of contents"
    )
    parser.add_argument('-s', '--sheet', default='Decreet 25.04.14',
                        help='Worksheet name. Default is "Decreet 25.04.14".',
                        choices=['Decreet 25.04.14', '(to be completed)'])
    args = parser.parse_args()
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    # items is the list of components that have been handled.
    items = []
    ns = neostore.NeoStore(cfg)
    # Get all book - titel nodes and relations for book
    component_list = ns.get_components_book('book', blabel=args.sheet)
    for comp in component_list.iterrows():
        comp_id = comp[1]['rid']
        toc = "{}.".format(comp[1]['rnr'])
        logging.debug("{toc} {label}".format(toc=toc, label=comp[1]['rlabel']))
        delve_into(comp_id, toc)
    logging.info('End Application')
