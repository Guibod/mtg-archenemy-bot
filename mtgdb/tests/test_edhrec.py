import unittest

from mtgdb.edhrec import EdhRec


class TestEdhrec(unittest.TestCase):
    def test_sanitize(self):
        self.assertEqual("reflecting-pool", EdhRec.sanitize("Reflecting Pool"))
        self.assertEqual("talisman-of-dominance", EdhRec.sanitize("Talisman of Dominance"))
        self.assertEqual("geier-reach-sanitarium", EdhRec.sanitize("Geier Reach Sanitarium"))
        self.assertEqual("witchs-cottage", EdhRec.sanitize("Witch's Cottage"))
        self.assertEqual("kayas-ghostform", EdhRec.sanitize("Kaya's Ghostform"))
        self.assertEqual("lim-duls-vault", EdhRec.sanitize("Lim-Dûl's Vault"))
        self.assertEqual("plus-2-mace", EdhRec.sanitize("+2 Mace"))
        self.assertEqual("deja-vu", EdhRec.sanitize("déjà-vu"))
