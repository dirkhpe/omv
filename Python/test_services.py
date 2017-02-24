"""
This script will test the Services.
"""

import logging
# import sys
import zeep
from lib import my_env


dossier_wsdl = "https://services-oefen.omgevingsloket.be/cxf/omgeving/ws/GeefDossierDienst/v1?wsdl"
project_wsdl = "https://services-oefen.omgevingsloket.be/cxf/omgeving/ws/GeefProjectDienst/v1?wsdl"

if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    dossier = zeep.Client(wsdl=dossier_wsdl)
    print(dossier.service.geefDossier(dossierUuid="EvjLmxHZT1WUvmcWqebhAQ", context=""))
    project = zeep.Client(wsdl=project_wsdl)
    print(project.service.servicename())
    logging.info('End Application')
