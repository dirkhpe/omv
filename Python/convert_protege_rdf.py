"""
This script will read a RDF file created by Protege and extract information.

The script will work on the extract of the instances. The classes are not yet processed.

Data will be converted in a component table and a relations table.

Structure of the Instances RDF file:
- Each element in the RDF Tree has a tag, attributes and children.
- The tag is the type of the component.
- The attribute is one of 3 types:
    {http://www.w3.org/1999/02/22-rdf-syntax-ns#}about: Unique identifier of the instance
    {http://www.w3.org/2000/01/rdf-schema#}label: Label in the Instance View
    {http://protege.stanford.edu/rdf}abcdef: Field, where abcdef is field name. Field value is short.

For a child there are 2 possibilities:
    Text available: the tag is field name, text is field value. Field value more than specific length. Normally
    attributes are empty then, but not always. In case text has special characters then attribute will be 'preserve'.
    Attributes and no text: tag is relation type, attribute resource value is target of the link.
"""

import logging
# import os
# import sys
from lib.datastore import DataStore
from lib import my_env
import xml.etree.ElementTree as Et

# ignore_rel_types = ["heeft_dossiertype",
#                     "heeft_procedurestap",
#                     "heeft_stap"]
ignore_rel_types = []


def strip_rdf(rdf, name):
    """
    This function will strip rdf identifier from the string
    @param rdf: rdf identifier to map
    @param name: Object with the rdf identifier
    @return: object without the rdf identifier
    """
    # Check if uri is part of the name:
    if rdf == name[0:len(rdf)]:
        short_name = name[len(rdf):]
    else:
        logging.error("*{rdf}* expected, but not found: *{name}*".format(rdf=rdf, name=name))
        short_name = "Undefined"
    return short_name


def strip_name_id(name):
    """
    This function will strip name identifier from Protege Name. The name identifier is terminated with ' * '. This is
    used to group items in the protege overview.
    @param name:
    @return:
    """
    delim = " * "
    if name.find(delim) > 0:
        rem_length = name.find(delim) + len(delim)
        return name[rem_length:]
    else:
        return name


def handle_instances(cfg):
    """
    This function handles the RDF file.
    @param cfg: Full path name of the file.
    @return:
    """
    rdf_file = cfg["Files"]["instances"]
    tree = Et.parse(rdf_file)
    root = tree.getroot()
    for el in root:
        # Reset and initialize row dictionary
        rowdict = {"class": strip_rdf(rdf_value, el.tag)}
        logging.debug("Element attribs: {attrib}".format(attrib=el.attrib))
        # First handle element attributes
        for k, v in el.attrib.items():
            # Get type of attribute item
            if rdf_id == k[0:len(rdf_id)]:
                rowdict["protege_id"] = strip_rdf(rdf_prot_id, v)
            elif rdf_value == k[0:len(rdf_value)]:
                rowdict[strip_rdf(rdf_value, k)] = v
            elif rdf_label == k[0:len(rdf_label)]:
                pass
            else:
                logging.error("Unknown element attribute type {k} with value {v}".format(k=k, v=v))
        # Then handle element children
        # Make sure I have my protege_id
        if "protege_id" not in rowdict:
            logging.error("Could not find Protege ID in attributes *{attrib}*".format(attrib=el.attrib))
            break
        for child in el:
            logging.debug("Child: {child}".format(child=child))
            if child.text is None:
                # No text is available, so this better is a relation.
                rel = {"rel_type": strip_rdf(rdf_value, child.tag),
                       "source":   rowdict["protege_id"],
                       "target":   strip_rdf(rdf_prot_id, child.attrib[resource_key])}
                if rel["rel_type"] in ignore_rel_types:
                    logging.debug("Ignore relation type {rt} for {pi}"
                                  .format(rt=rel["rel_type"], pi=rowdict["protege_id"]))
                else:
                    ds.insert_row("relations", rel)
            else:
                # No attributes, so this is key/value with value longer than in element attribute
                # This can be label as well, in which case it can be ignored
                # So check on rdf_value only
                if rdf_value == child.tag[0:len(rdf_value)]:
                    rowdict[strip_rdf(rdf_value, child.tag)] = child.text
        # Check to remove identifier from naam:
        try:
            rowdict['label'] = rowdict['naam']
            rowdict['naam'] = strip_name_id(rowdict["naam"])
        except KeyError:
            pass
        ds.insert_row("components", rowdict)


if __name__ == "__main__":
    config = my_env.init_env("convert_protege", __file__)
    ds = DataStore(config)
    ds.clear_tables()
    # Initialize rdf identifiers
    rdf_id = config["uris"]["rdf_id"]
    rdf_label = config["uris"]["rdf_label"]
    rdf_value = config["uris"]["rdf_value"]
    rdf_prot_id = config["uris"]["rdf_prot_id"]
    resource_key = config["uris"]["resource_key"]
    handle_instances(config)
