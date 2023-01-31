import unittest

from mtgdb.color import MagicColorPie, White, Black, Blue, Red, Green, Color, IdentityMap, ColorList, ColorPie, \
    Identity, MagicIdentities

Purple = Color("p")


class TestIdentityMap(unittest.TestCase):
    def setUp(self) -> None:
        self.pie = ColorPie(Blue, Red)
        self.idmap = IdentityMap(self.pie)
        monoU = Identity(self.pie, [Blue])
        self.idmap.add(monoU)

    def test_key_access_as_identity_object(self):
        self.assertIn(Identity(self.pie, [Blue]), self.idmap)

    def test_key_access_as_string(self):
        self.assertIn("u", self.idmap)

    def test_key_access_as_checksum(self):
        self.assertIn(1, self.idmap)

    def test_key_access_bad_identity_object(self):
        self.assertNotIn(Identity(self.pie, [Red]), self.idmap)

    def test_key_access_bad_checksum(self):
        self.assertNotIn(100, self.idmap)

    def test_key_access_bad_string(self):
        self.assertNotIn("r", self.idmap)


class TestColorPie(unittest.TestCase):
    def test_length(self):
        pie = ColorPie(Red, Blue, Purple)
        self.assertEqual(3, len(pie))

    def test_length_with_duplicates(self):
        with self.assertRaises(ValueError):
            ColorPie(Red, Blue, Purple, Blue)

    def test_parse_identity(self):
        pie = ColorPie(Red, Blue, Purple)

        self.assertEqual(pie.parse("rp"), Identity(pie, [Red, Purple]))

    def test_access(self):
        pie = ColorPie(Red, Blue, Purple)

        self.assertIs(pie[0], Red)
        self.assertIs(pie[1], Blue)
        self.assertIs(pie[2], Purple)

    def test_next_NONE(self):
        pie = ColorPie(Blue, Red, Green, Purple)

        self.assertEqual(pie.shift(Blue), Red)
        self.assertEqual(pie.shift(Red), Green)
        self.assertEqual(pie.shift(Green), Purple)
        self.assertEqual(pie.shift(Purple), Blue)

    def test_next_1(self):
        pie = ColorPie(Blue, Red, Green, Purple)

        self.assertEqual(pie.shift(Blue, 1), Red)
        self.assertEqual(pie.shift(Red, 1), Green)
        self.assertEqual(pie.shift(Green, 1), Purple)
        self.assertEqual(pie.shift(Purple, 1), Blue)

    def test_next_2(self):
        pie = ColorPie(Blue, Red, Green, Purple)

        self.assertEqual(pie.shift(Blue, 2), Green)
        self.assertEqual(pie.shift(Red, 2), Purple)
        self.assertEqual(pie.shift(Green, 2), Blue)
        self.assertEqual(pie.shift(Purple, 2), Red)

    def test_prev_1(self):
        pie = ColorPie(Blue, Red, Green, Purple)

        self.assertEqual(pie.shift(Blue, -1), Purple)
        self.assertEqual(pie.shift(Red, -1), Blue)
        self.assertEqual(pie.shift(Green, -1), Red)
        self.assertEqual(pie.shift(Purple, -1), Green)

    def test_combinations_with_one_color_pie(self):
        pie = ColorPie(Blue)
        combi = pie.combinations()
        self.assertEqual(len(combi), 2)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 2)
        self.assertIn(Identity(pie, []), idmap)
        self.assertIn("", idmap)
        self.assertIn(Identity(pie, [Blue]), idmap)
        self.assertIn("u", idmap)

    def test_combinations_with_two_color_pie(self):
        pie = ColorPie(Blue, Red)
        combi = pie.combinations()
        self.assertEqual(len(combi), 4)

        idmap = pie.build_identity_map()

        self.assertEqual(len(idmap), 4)
        self.assertIn("", idmap)
        self.assertIn(Identity(pie, [Blue]), idmap)
        self.assertIn(Identity(pie, [Red]), idmap)
        self.assertIn(Identity(pie, [Blue, Red]), idmap)

    def test_combinations_with_three_color_pie(self):
        pie = ColorPie(Blue, Red, Green)

        combi = pie.combinations()
        self.assertEqual(len(combi), 8)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 8)
        self.assertIn(Identity(pie, []), idmap)
        self.assertIn(Identity(pie, [Blue]), idmap)
        self.assertIn(Identity(pie, [Red]), idmap)
        self.assertIn(Identity(pie, [Green]), idmap)
        self.assertIn(Identity(pie, [Blue, Red]), idmap)
        self.assertIn(Identity(pie, [Red, Green]), idmap)
        self.assertIn(Identity(pie, [Green, Red]), idmap)
        self.assertIn(Identity(pie, [Blue, Red, Green]), idmap)

    def test_combinations_with_four_color_pie(self):
        pie = ColorPie(Blue, Black, Red, Green)

        combi = pie.combinations()
        self.assertEqual(len(combi), 16)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 16)
        self.assertIn("", idmap)
        self.assertIn("u", idmap)
        self.assertIn("b", idmap)
        self.assertIn("r", idmap)
        self.assertIn("g", idmap)
        self.assertIn("ub", idmap)
        self.assertIn("br", idmap)
        self.assertIn("rg", idmap)
        self.assertIn("gu", idmap)
        self.assertIn("ur", idmap)
        self.assertIn("bg", idmap)
        self.assertIn("ubr", idmap)
        self.assertIn("brg", idmap)
        self.assertIn("rgu", idmap)
        self.assertIn("urbg", idmap)

    def test_combinations_with_five_color_pie(self):
        pie = ColorPie(White, Blue, Black, Red, Green,)

        combi = pie.combinations()
        self.assertEqual(len(combi), 32)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 32)

    def test_combinations_with_six_color_pie(self):
        pie = ColorPie(White, Blue, Black, Red, Green, Purple)

        combi = pie.combinations()
        self.assertEqual(len(combi), 64)

        idmap = pie.build_identity_map()
        self.assertEqual(len(idmap), 64)


class TestIdentity(unittest.TestCase):
    def setUp(self) -> None:
        self.pie = ColorPie(Blue, Red, Purple, White)

    def test_empty(self):
        id1 = Identity(self.pie, [])
        self.assertEqual(id1.checksum(), 0b00)
        cl2 = Identity(self.pie, [])
        self.assertEqual(id1.checksum(), 0b00)

        self.assertEqual(id1, cl2)

    def test_size_1(self):
        id1 = Identity(self.pie, [Blue])
        self.assertEqual(id1.checksum(), 0b01)
        cl2 = Identity(self.pie, [Blue])
        self.assertEqual(id1.checksum(), 0b01)

        self.assertEqual(id1, cl2)

    def test_size_2(self):
        id1 = Identity(self.pie, [Blue, Red])
        self.assertEqual(id1.checksum(), 0b11)
        id2 = Identity(self.pie, [Blue, Red])
        self.assertEqual(id1.checksum(), 0b11)
        id3 = Identity(self.pie, [Red, Blue])
        self.assertEqual(id3.checksum(), 0b11)

        self.assertEqual(id1, id2)
        self.assertEqual(id2, id3)
        self.assertEqual(id1, id3)
        
    def test_canonical(self):
        id1 = Identity(self.pie, [Blue, Red])
        self.assertEqual(id1.canonical, "ur")
        id2 = Identity(self.pie, [Red, Blue])
        self.assertEqual(id2.canonical, "ru")
        id3 = Identity(self.pie, [Red, Blue, Purple])
        self.assertEqual(id3.canonical, "rup")

    def test_name(self):
        id1 = Identity(self.pie, [Blue, Red])
        self.assertEqual(id1.name, "ur")

        id1.describe(name="Izzet League")
        self.assertEqual(id1.name, "Izzet League")

        id1.describe("Izzet")
        self.assertEqual(id1.name, "Izzet")
        self.assertEqual(id1.aliases, [])

    def test_aliases(self):
        id1 = Identity(self.pie, [Blue, Red])
        self.assertEqual(id1.aliases, [])

        id1.describe("fu", ["Izzet League"])
        self.assertEqual(id1.aliases, ["Izzet League"])

        id1.describe(aliases=["Prismari"])
        self.assertEqual(id1.aliases, ["Izzet League", "Prismari"])


class TestMagicColorPie(unittest.TestCase):
    def test_colorpie_size(self):
        self.assertEqual(len(MagicColorPie), 5)

    def test_colorpie_combinations(self):
        combinations = MagicColorPie.combinations()

        self.assertEqual(len(combinations), 32)

    def test_colorpie_index(self):
        self.assertIs(MagicColorPie[0], White)
        self.assertIs(MagicColorPie[1], Blue)
        self.assertIs(MagicColorPie[2], Black)
        self.assertIs(MagicColorPie[3], Red)
        self.assertIs(MagicColorPie[4], Green)


class TestMagicIdentities(unittest.TestCase):
    def test_colorpie_access_guild_by_canonical(self):
        self.assertEqual(MagicIdentities["rb"].name, "Rakdos")
        self.assertEqual(MagicIdentities["wu"].name, "Azorius")

    def test_colorpie_access_guild_by_non_canonical(self):
        self.assertEqual(MagicIdentities["br"].name, "Rakdos")
        self.assertEqual(MagicIdentities["uw"].name, "Azorius")

    def test_colorpie_access_guild_by_identity(self):
        self.assertEqual(MagicIdentities[Identity(MagicColorPie, [Red, Black])].name, "Rakdos")
        self.assertEqual(MagicIdentities[Identity(MagicColorPie, [White, Blue])].name, "Azorius")

    def test_colorpie_access_guild_by_name(self):
        self.assertEqual(MagicIdentities["cult OF RAKDOS"].name, "Rakdos")
        self.assertEqual(MagicIdentities["Azorius SENATE"].name, "Azorius")

    def test_canonicals_colorless(self):
        self.assertEqual("colorless", MagicIdentities[""].canonical, "colorless")

    def test_canonicals_mono_color(self):
        self.assertEqual("w", MagicIdentities["w"].canonical)
        self.assertEqual("u", MagicIdentities["u"].canonical)
        self.assertEqual("b", MagicIdentities["b"].canonical)
        self.assertEqual("r", MagicIdentities["r"].canonical)
        self.assertEqual("g", MagicIdentities["g"].canonical)

    def test_canonicals_allied_guilds(self):
        self.assertEqual("wu", MagicIdentities["wu"].canonical)
        self.assertEqual("ub", MagicIdentities["ub"].canonical)
        self.assertEqual("br", MagicIdentities["br"].canonical)
        self.assertEqual("rg", MagicIdentities["rg"].canonical)
        self.assertEqual("gw", MagicIdentities["gw"].canonical)

    def test_canonicals_enemy_guilds(self):
        self.assertEqual("wb", MagicIdentities["wb"].canonical)
        self.assertEqual("ur", MagicIdentities["ur"].canonical)
        self.assertEqual("bg", MagicIdentities["bg"].canonical)
        self.assertEqual("rw", MagicIdentities["rw"].canonical)
        self.assertEqual("gu", MagicIdentities["gu"].canonical)

    def test_canonicals_shards(self):
        self.assertEqual("wub", MagicIdentities["wub"].canonical)
        self.assertEqual("ubr", MagicIdentities["ubr"].canonical)
        self.assertEqual("brg", MagicIdentities["brg"].canonical)
        self.assertEqual("rgw", MagicIdentities["rgw"].canonical)
        self.assertEqual("gwu", MagicIdentities["gwu"].canonical)

    def test_canonicals_wedges(self):
        self.assertEqual("wbg", MagicIdentities["wbg"].canonical)
        self.assertEqual("urw", MagicIdentities["urw"].canonical)
        self.assertEqual("bgu", MagicIdentities["bgu"].canonical)
        self.assertEqual("rwb", MagicIdentities["rwb"].canonical)
        self.assertEqual("gur", MagicIdentities["gur"].canonical)

    def test_canonicals_4colors(self):
        self.assertEqual("wubr", MagicIdentities["wubr"].canonical)
        self.assertEqual("ubrg", MagicIdentities["ubrg"].canonical)
        self.assertEqual("brgw", MagicIdentities["brgw"].canonical)
        self.assertEqual("rgwu", MagicIdentities["rgwu"].canonical)
        self.assertEqual("gwub", MagicIdentities["gwub"].canonical)

    def test_canonical_5c(self):
        self.assertEqual("wubrg", MagicIdentities["wubrg"].canonical)


class TestColor(unittest.TestCase):
    def test_white(self):
        self.assertEqual(str(White), "{W}")

    def test_blue(self):
        self.assertEqual(str(Blue), "{U}")

    def test_black(self):
        self.assertEqual(str(Black), "{B}")

    def test_red(self):
        self.assertEqual(str(Red), "{R}")

    def test_green(self):
        self.assertEqual(str(Green), "{G}")
