"""
This script will test the Services.
"""

import logging
# import sys
import zeep
from lib import my_env


crab_wsdl = "http://crab.agiv.be/wscrab/wscrab.svc?wsdl"

if __name__ == "__main__":
    cfg = my_env.init_env("convert_protege", __file__)
    crab = zeep.Client(wsdl=crab_wsdl)
    print(crab.service.FindGemeenten(GemeenteNaam="Oostende", GewestId=2, SorteerVeld=1))
    logging.info('End Application')
