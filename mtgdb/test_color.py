import unittest

from mtgdb.color import ColorPie, White, Black, Blue, Red, Green, Color, IdentityMap, ColorList

Purple = Color("P")


class TestColorList(unittest.TestCase):
    def test_equality_empty(self):
        a = ColorList()
        b = ColorList()
        self.assertEqual(a, b)

    def test_equality_not_empty(self):
        a = ColorList(White, Blue, Red)
        b = ColorList(White, Blue, Red)
        self.assertEqual(a, b)

    def test_equality_not_equal(self):
        a = ColorList(White, Blue, Red)
        b = ColorList(White, Blue, Red, Red)
        self.assertNotEqual(a, b)

    def test_list_length(self):
        c = ColorList()
        self.assertEqual(len(c), 0)

        c = ColorList(Blue, Blue)
        self.assertEqual(len(c), 2)

    def test_list_unique(self):
        c = ColorList(Blue, Blue)
        self.assertEqual(len(c), 2)

        c2 = c.unique()
        self.assertEqual(len(c2), 1)
        self.assertIsNot(c, c2)

    def test_list_order(self):
        c = ColorList(Green, Blue, Green)
        c2 = c.sort(ColorPie)
        self.assertEqual(len(c2), 3)
        self.assertIsNot(c, c2)
        self.assertIsNot(c, c2)


class TestIdentityMap(unittest.TestCase):
    def test_size(self):
        idmap = IdentityMap(ColorPie)
        self.assertEqual(len(idmap), 32)

    def test_key_key_str_access(self):
        idmap = IdentityMap(ColorPie)
        self.assertIn("W", idmap.keys())
        self.assertEqual(idmap["W"].colors, ColorList(White))

    def test_key_color_tuple_access(self):
        idmap = IdentityMap(ColorPie)
        self.assertIn((White, ), idmap.keys())
        self.assertEqual(idmap[(White, )].colors, ColorList(White))

    def test_key_color_list_access(self):
        idmap = IdentityMap(ColorPie)
        self.assertIn([White], idmap.keys())
        self.assertEqual(idmap[[White]].colors, ColorList(White))

    def test_key_deduplicate(self):
        idmap = IdentityMap(ColorPie)
        self.assertEqual("W", idmap.build_key(ColorList(White, White)))

    def test_key_multicolor(self):
        idmap = IdentityMap(ColorPie)
        self.assertEqual("WRG", idmap.build_key(ColorList(White, Red, Green)))

    def test_key_multicolor_deduplicate(self):
        idmap = IdentityMap(ColorPie)
        self.assertEqual("WRG", idmap.build_key(ColorList(Red, White, Red, Green)))

    def test_key_multicolor_sorts(self):
        idmap = IdentityMap(ColorPie)
        self.assertEqual("WRG", idmap.build_key(ColorList(Red, Green, White)))


class TestColorPie(unittest.TestCase):
    def test_colorpie_size(self):
        self.assertEqual(len(ColorPie), 5)

    def test_colorpie_combinations(self):
        combinations = ColorPie.combinations()

        self.assertEqual(len(combinations), 32)

    def test_colorpie_access_guild(self):
        self.assertEqual(ColorPie.identities["rakdos"].name, "Rakdos")
        self.assertEqual(ColorPie.identities["Rakdos"].name, "Rakdos")
        self.assertEqual(ColorPie.identities["Cult Of Rakdos"].name, "Rakdos")
        self.assertEqual(ColorPie.identities["cult of rakDOS"].name, "Rakdos")

    def test_colorpie_index(self):
        self.assertIs(ColorPie[0], White)
        self.assertIs(ColorPie[1], Blue)
        self.assertIs(ColorPie[2], Black)
        self.assertIs(ColorPie[3], Red)
        self.assertIs(ColorPie[4], Green)

    def test_allied_purple(self):
        with self.assertRaises(ValueError):
            ColorPie.allied(White, Purple)

    def test_enemy_purple(self):
        with self.assertRaises(ValueError):
            ColorPie.enemy(White, Purple)

    def test_allied_white(self):
        self.assertFalse(ColorPie.allied(White, White))
        self.assertTrue(ColorPie.allied(White, Blue))
        self.assertFalse(ColorPie.allied(White, Black))
        self.assertFalse(ColorPie.allied(White, Red))
        self.assertTrue(ColorPie.allied(White, Green))

    def test_enemy_white(self):
        self.assertFalse(ColorPie.enemy(White, White))
        self.assertFalse(ColorPie.enemy(White, Blue))
        self.assertTrue(ColorPie.enemy(White, Black))
        self.assertTrue(ColorPie.enemy(White, Red))
        self.assertFalse(ColorPie.enemy(White, Green))

    def test_allied_blue(self):
        self.assertTrue(ColorPie.allied(Blue, White))
        self.assertFalse(ColorPie.allied(Blue, Blue))
        self.assertTrue(ColorPie.allied(Blue, Black))
        self.assertFalse(ColorPie.allied(Blue, Red))
        self.assertFalse(ColorPie.allied(Blue, Green))

    def test_enemy_blue(self):
        self.assertFalse(ColorPie.enemy(Blue, White))
        self.assertFalse(ColorPie.enemy(Blue, Blue))
        self.assertFalse(ColorPie.enemy(Blue, Black))
        self.assertTrue(ColorPie.enemy(Blue, Red))
        self.assertTrue(ColorPie.enemy(Blue, Green))

    def test_allied_black(self):
        self.assertFalse(ColorPie.allied(Black, White))
        self.assertTrue(ColorPie.allied(Black, Blue))
        self.assertFalse(ColorPie.allied(Black, Black))
        self.assertTrue(ColorPie.allied(Black, Red))
        self.assertFalse(ColorPie.allied(Black, Green))

    def test_enemy_black(self):
        self.assertTrue(ColorPie.enemy(Black, White))
        self.assertFalse(ColorPie.enemy(Black, Blue))
        self.assertFalse(ColorPie.enemy(Black, Black))
        self.assertFalse(ColorPie.enemy(Black, Red))
        self.assertTrue(ColorPie.enemy(Black, Green))

    def test_allied_red(self):
        self.assertFalse(ColorPie.allied(Red, White))
        self.assertFalse(ColorPie.allied(Red, Blue))
        self.assertTrue(ColorPie.allied(Red, Black))
        self.assertFalse(ColorPie.allied(Red, Red))
        self.assertTrue(ColorPie.allied(Red, Green))

    def test_enemy_red(self):
        self.assertTrue(ColorPie.enemy(Red, White))
        self.assertTrue(ColorPie.enemy(Red, Blue))
        self.assertFalse(ColorPie.enemy(Red, Black))
        self.assertFalse(ColorPie.enemy(Red, Red))
        self.assertFalse(ColorPie.enemy(Red, Green))

    def test_allied_green(self):
        self.assertTrue(ColorPie.allied(Green, White))
        self.assertFalse(ColorPie.allied(Green, Blue))
        self.assertFalse(ColorPie.allied(Green, Black))
        self.assertTrue(ColorPie.allied(Green, Red))
        self.assertFalse(ColorPie.allied(Green, Green))

    def test_enemy_green(self):
        self.assertFalse(ColorPie.enemy(Green, White))
        self.assertTrue(ColorPie.enemy(Green, Blue))
        self.assertTrue(ColorPie.enemy(Green, Black))
        self.assertFalse(ColorPie.enemy(Green, Red))
        self.assertFalse(ColorPie.enemy(Green, Green))


class TestColor(unittest.TestCase):
    def test_white(self):
        self.assertEqual("{}".format(White), "{W}")
        self.assertTrue(White.allied(Green))
        self.assertTrue(White.allied(Blue))
        self.assertTrue(White.enemy(Black))
        self.assertTrue(White.enemy(Red))

    def test_blue(self):
        self.assertEqual("{}".format(Blue), "{U}")
        self.assertTrue(Blue.allied(White))
        self.assertTrue(Blue.allied(Black))
        self.assertTrue(Blue.enemy(Red))
        self.assertTrue(Blue.enemy(Green))

    def test_black(self):
        self.assertEqual("{}".format(Black), "{B}")
        self.assertTrue(Black.enemy(White))
        self.assertTrue(Black.allied(Blue))
        self.assertTrue(Black.allied(Red))
        self.assertTrue(Black.enemy(Green))

    def test_red(self):
        self.assertEqual("{}".format(Red), "{R}")
        self.assertTrue(Red.enemy(White))
        self.assertTrue(Red.enemy(Blue))
        self.assertTrue(Red.allied(Black))
        self.assertTrue(Red.allied(Green))

    def test_green(self):
        self.assertEqual("{}".format(Green), "{G}")
        self.assertTrue(Green.allied(White))
        self.assertTrue(Green.enemy(Blue))
        self.assertTrue(Green.enemy(Black))
        self.assertTrue(Green.allied(Red))
