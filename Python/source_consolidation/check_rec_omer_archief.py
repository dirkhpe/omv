"""
This script report on one dossiertype - fase - gebeurtenis - document record as found in omer database.
It will report on translations to components from Archief. The purpose is to find where translation fails.
"""

# Allow lib to library import path.
import os
import sys
(pp, cd) = os.path.split(os.getcwd())
sys.path.append(pp)

# import logging
import argparse
import os
from datetime import datetime as dt
from lib import my_env
from lib import mysqlstore as mysql
from lib.mysqlstore import *

not_translated = " . "


def list_of_tx2ar(omcomp, comp_id, rel_table=None, prev_comp_id=None, label=None, pn=None):
    """
    This function will get all the translations for a specific Omer component. In case there is one or more
    translation in the Archief, a list of all translations will be provided.
    In case there is no translation, then a list with a single value (" . ") will be provided. This way we are sure
    that the OMER Component is listed.

    :param omcomp: Class for the OMER Component (UpType, UpFase, UpGebeurtenis, UpDocument)

    :param comp_id: ID for the OMER component

    :param rel_table: Archief Relation class (table) from higher level component to required component. None for Type.

    :param prev_comp_id: If higher-level component is not translated, then this component does not need to be
    translated. If the higher-level component is translated, then I need the ID of the higher-level component. This
    (lower-level) component must be in the list of possibilities (arfase2type, arstap2fase, ardocument2stap). The list
    of translations must be the cross-cut of Archief possibilities and Uitwisselingsplatform to Archief possibilities.

    :param label:

    :param pn: Name of the previous level

    :return: List of translations, in tuples (component ID, component name)
    """
    # First find name which I'm trying to translate.
    comp = cons_sess.query(omcomp).filter_by(id=comp_id).one()
    line = "\nOnderzoek vertalingen voor {l}: *{comp}* gekoppeld met *{pn}*\n".format(l=label, comp=comp.naam, pn=pn)
    fh.write(line)
    list_tx = []
    if prev_comp_id != -1:
        # Limit the list of component possibilities. They must be in the Archief possibilities.
        # Limit this list for all components below Type.
        if rel_table:
            qry = cons_sess.query(rel_table).filter_by(target_id=prev_comp_id)
            item_ids = [item.source_id for item in qry.all()]
            line = "Archief Koppelingen: {i}\n".format(i=item_ids)
            fh.write(line)
        for arcomps in cons_sess.query(omcomp).filter_by(id=comp_id).filter(omcomp.arcomps.any()):
            for arcomp in arcomps.arcomps:
                if rel_table:
                    if arcomp.id in item_ids:
                        list_tx.append((arcomp.id, arcomp.naam))
                        line = "Vertaling gevonden: {n}\n".format(n=arcomp.label)
                    else:
                        line = "Vertaling niet in Archief Koppelingen: {n}\n".format(n=arcomp.label)
                    fh.write(line)
                else:
                    # Relation table does not exist, so must be Type. Accept the translation
                    list_tx.append((arcomp.id, arcomp.naam))
                    line = "Vertaling gevonden: {n}\n".format(n=arcomp.naam)
                    fh.write(line)
    if len(list_tx) == 0:
        list_tx.append((-1, not_translated))
        line = "Geen vertaling gevonden voor {l}\n".format(l=label)
        fh.write(line)
    return list_tx


def gebeurtenis2stap(gebeurtenis_id, prev_comp_id=None):
    """
    This function will translate the gebeurtenis to upstap and returns a list of upstap_ids that can be used in
    list_of_tx2ar, to go from upstap to arstap.

    :param gebeurtenis_id: ID of the gebeurtenis

    :param prev_comp_id: If higher-level component is not translated, then this component does not need to be
    translated.

    :return: upstap_id associated with the gebeurtenis.



    """
    if prev_comp_id != -1:
        upgeb = cons_sess.query(UpGebeurtenis).filter_by(id=gebeurtenis_id).one()
        fh.write("\nOnderzoek vertaling Gebeurtenis: *{g}*\n".format(g=upgeb.naam))
        if upgeb.upstap:
            fh.write("Gebeurtenis vertaald naar Loket stap *{s}*\n".format(s=upgeb.upstap.naam))
            return upgeb.upstap.id, upgeb.upstap.naam
    fh.write("Gebeurtenis niet vertaald naar Loket stap.\n")
    return -1, not_translated


if __name__ == "__main__":

    # Configure Command line arguments
    parser = argparse.ArgumentParser(
            description="Script to check a specific omercombi record."
    )
    parser.add_argument('-r', '--recid', type=int, required=True,
                        help='Record ID for the record in omercombi to check.')
    args = parser.parse_args()
    items = []
    cfg = my_env.init_env("convert_protege", __file__)
    logging.info("Arguments: {a}".format(a=args))

    now = dt.now().strftime("%Y%m%d%H%M%S")

    # Get session for Consolidation Database
    cons_sess = mysql.init_session(db=cfg["ConsolidationDB"]["db"],
                                   user=cfg["ConsolidationDB"]["user"],
                                   pwd=cfg["ConsolidationDB"]["pwd"],
                                   echo=False)

    # Set-up files and remove previous version of the file.
    repname = "Check Record {recid}".format(recid=args.recid)
    fn = os.path.join(cfg['Main']['reportdir'], "{r} {now}.txt".format(r=repname, now=now))

    fh = open(fn, 'w')

    # First get query based on DossierType

    omercombi = cons_sess.query(OmerCombi).filter_by(id=args.recid).one()

    uptype = omercombi.uptype.naam
    upfase = omercombi.upfase.naam
    upgebeurtenis = omercombi.upgebeurtenis.naam
    updocument = omercombi.updocument.naam
    ln = "Type: {t}\nFase: {f}\nGebeurtenis: {g}\nDocument: {d}\n\n\n".format(t=uptype, f=upfase,
                                                                           g=upgebeurtenis, d=updocument)
    fh.write(ln)
    artypes = list_of_tx2ar(UpType, omercombi.uptype.id, label="Type", pn="")

    # Additional step to get ArFase ID.
    (upstap_id, upstap_naam) = gebeurtenis2stap(omercombi.upgebeurtenis.id, upfase)
    for (arfase_id, arfase_naam) in list_of_tx2ar(UpFase, omercombi.upfase_id, ArFase2Type, artypes[0][0], 'Fase',
                                                  pn=uptype):
        for (arstap_id, arstap_naam) in list_of_tx2ar(UpStap, upstap_id, ArStap2Fase, arfase_id, 'Stap',
                                                      pn=arfase_naam):
            for (ardoc_id, ardoc_naam) in list_of_tx2ar(UpDocument, omercombi.updocument.id,
                                                        ArDocument2Stap, arstap_id, 'Document', pn=arstap_naam):
                ln = "\nOnderzoek volgende stap\n"
                fh.write(ln)

    fh.close()

logging.info('End Application')
