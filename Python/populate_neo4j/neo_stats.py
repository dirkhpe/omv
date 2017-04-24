"""
This procedure will get statistics and will do some error checking.
"""

# import logging
import unittest
from lib import my_env
from lib import neostore


class TestNeoStore(unittest.TestCase):

    def setUp(self):
        # Initialize Environment
        cfg = my_env.init_env("convert_protege", __file__)
        # Get NeoStore object
        self.ns = neostore.NeoStore(cfg)

    def test_contents(self):
        nodes = {
                'Dossiertype': 14,
                'ProcedureFase': 20,
                'ProcedureStap': 33,
                'Document': 214,
                'Artikel': 86,
                'Boek': 2,
                'Titel': 10,
                'Hoofdstuk': 46,
                'Afdeling': 99,
                'Onderafdeling': 49,
                'Aanleg': 3
        }
        for k, v in nodes.items():
            self.assertEqual(self.ns.calc_nodes(k), v, "{k}".format(k=k))

    def get_to_orphan(self):
        mand_rels = [('ProcedureStap', 'bij_procedurestap'),
                     ('Dossiertype', 'voor_dossiertype'),
                     ('ProcedureFase', 'in_procedure')]
        resline = ""
        for mand_rel in mand_rels:
            df = self.ns.get_nodes_to_orphan(mand_rel[0], mand_rel[1])
            if not df.empty:
                resline += "To orphan(s) in {t} - {r}:\n{res}".format(res=resline,
                                                                      t=mand_rel[0],
                                                                      r=mand_rel[1])
                for node in df.iterrows():
                    resline += "{n} ({l})\n".format(n=node[1]['naam'], l=node[1]['label'])
        return resline

    def get_from_orphan(self):
        mand_rels = [('Document', 'bij_procedurestap'),
                     ('ProcedureFase', 'voor_dossiertype'),
                     ('ProcedureStap', 'in_procedure')]
        resline = ""
        for mand_rel in mand_rels:
            df = self.ns.get_nodes_from_orphan(mand_rel[0], mand_rel[1])
            if not df.empty:
                resline += "From orphan(s) in {t} - {r}:\n{res}".format(res=resline,
                                                                        t=mand_rel[0],
                                                                        r=mand_rel[1])
                for node in df.iterrows():
                    resline += "{n} ({l})\n".format(n=node[1]['naam'], l=node[1]['label'])
        return resline

    def test_to_orphan_nodes(self):
        res = self.get_to_orphan()
        self.assertEqual(res, "", "{res}".format(res=res))

    def test_from_orphan_nodes(self):
        res = self.get_from_orphan()
        self.assertEqual(res, "", "{res}".format(res=res))

if __name__ == "__main__":
    unittest.main()
