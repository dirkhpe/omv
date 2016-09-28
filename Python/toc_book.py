"""
This script will get the explorer-like graph for a book. It will get the book label and calculate the path down.
"""

import argparse
import logging
import os
from lib import neostore
from lib import my_env


def write_nice(ind, item, pg):
    if args.nopagenumber:
        blz = ""
    else:
        dots = 90 - len(ind) - len(item) - len("{}".format(pg))
        dl = "." * dots
        blz = " {dl} {pg}".format(dl=dl, pg=pg)
    fh.write("{ind} {item}{blz}\n".format(ind=ind, item=item, blz=blz))
    return


def delve_into(nid, dtoc):
    topics = ns.get_topics(nid)
    for topic in topics.iterrows():
        topic_id = topic[1]['rid']
        topic_toc = "{toc}{nr}.".format(toc=dtoc, nr=topic[1]['rnr'])
        write_nice(topic_toc, topic[1]['rlabel'], topic[1]['pagina'])
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
    parser.add_argument('--nopagenumber', action='store_true',
                        help='Do not print pagenumber in Table of Contents')
    args = parser.parse_args()
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))
    # items is the list of components that have been handled.
    items = []
    ns = neostore.NeoStore(cfg)
    # Get all book - titel nodes and relations for book
    component_list = ns.get_components_book('book', blabel=args.sheet)
    fn = os.path.join(cfg['Main']['graphdir'], "{}.txt".format(args.sheet))
    with open(fn, 'w') as fh:
        for comp in component_list.iterrows():
            comp_id = comp[1]['rid']
            toc = "{}.".format(comp[1]['rnr'])
            write_nice(toc, comp[1]['rlabel'], comp[1]['pagina'])
            delve_into(comp_id, toc)
    logging.info('End Application')
