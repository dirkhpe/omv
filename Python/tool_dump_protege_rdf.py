"""
This script will read a RDF file created by Protege and dump information in a text file.
This can be useful to understand structure of the information.
"""

import logging
import os
from lib import my_env
import xml.etree.ElementTree as Et


def init_env(projectname):
    projectname = projectname
    modulename = my_env.get_modulename(__file__)
    config = my_env.get_inifile(projectname, __file__)
    my_log = my_env.init_loghandler(config, modulename)
    my_log.info('Start Application')
    return config


def handle_instances(cfg):
    """
    This function handles the RDF file.
    @param cfg: Full path name of the file.
    @return:
    """
    rdf_file = cfg["Files"]["instances"]
    inst_file_dir = cfg["Main"]["logdir"]
    inst_file_name = "instances.txt"
    f = open(os.path.join(inst_file_dir, inst_file_name), mode='w')
    tree = Et.parse(rdf_file)
    root = tree.getroot()
    logging.info(("Root: ".format(root.attrib)))
    for child in root:
        f.write("Handling Element:\n")
        f.write("T: {}, A: {}\n".format(child.tag, child.attrib))
        for sc in child:
            f.write("Tag: {}, Attrib: {}, Text: {}\n".format(sc.tag, sc.attrib, sc.text))
        f.write("\n")
    f.close()


def main():
    cfg = init_env("convert_protege")
    handle_instances(cfg)


if __name__ == "__main__":
    main()
