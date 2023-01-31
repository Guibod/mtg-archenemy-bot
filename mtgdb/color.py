import itertools
from abc import abstractmethod
from functools import lru_cache
from typing import Union, Mapping, Iterator, Sequence, overload


class Color:
    def __init__(self, symbol):
        self.symbol: str = symbol

    def allied(self, color: "Color") -> bool:
        return ColorPie.allied(self, color)

    def enemy(self, color: "Color") -> bool:
        return ColorPie.enemy(self, color)

    def __str__(self):
        return "{" + self.symbol + "}"

    def __repr__(self):
        return "Color(" + self.symbol + ")"


class ColorList(Sequence[Color]):
    @overload
    @abstractmethod
    def __getitem__(self, s: slice) -> Sequence[Color]:
        return self.colors[s]

    def __getitem__(self, i: int) -> Color:
        return self.colors[i]

    def __len__(self) -> int:
        return len(self.colors)

    def __init__(self, *args: Color):
        self.colors = list(args)

    def sort(self, pie: "ColorPie"):
        return ColorList(*sorted(self.colors, key=lambda x: pie.colors.index(x)))

    def unique(self):
        return ColorList(*set(self.colors))

    def __repr__(self):
        return "ColorList({})".format("".join(map(repr, self.colors)))

    def __eq__(self, other):
        return self.colors == other.colors


class Pie(Sequence[Color]):
    """
    A color pie is a circular list of colors
    """

    def __getitem__(self, i):
        return self.colors[i]

    def __len__(self) -> int:
        return len(self.colors)

    def __iter__(self) -> Iterator[Color]:
        return iter(self.colors)

    def __init__(self, colors: ColorList):
        self.colors = colors
        self.identities = IdentityMap(self)

    @lru_cache
    def allied(self, a: Color, b: Color) -> bool:
        if a == b:
            return False
        return self.is_next_to(self.colors.index(a), self.colors.index(b))

    @lru_cache
    def enemy(self, a: Color, b: Color) -> bool:
        if a == b:
            return False
        return not self.is_next_to(self.colors.index(a), self.colors.index(b))

    @lru_cache
    def combinations(self) -> [ColorList]:
        out = []
        for i in range(0, len(self.colors) + 1):
            for colors in itertools.combinations(self.colors, i):
                out.append(ColorList(*colors))
        return out

    def is_next_to(self, a: int, b: int) -> bool:
        length = len(self.colors)

        return \
            b == (a + 1) % length or \
            b == (a + length - 1) % length

    def __hash__(self):
        return hash(tuple(self))


class IdentityMap(Mapping[Union[str, ColorList], "Identity"]):
    def __init__(self, pie: Pie):
        self.map = dict()
        self.pie = pie

        for colors in self.pie.combinations():
            key=self.build_key(colors)
            self.map[key] = Identity(colors)

    def __getitem__(self, k: Union[str, ColorList]) -> "Identity":
        if isinstance(k, tuple):
            k = ColorList(*k)
        if isinstance(k, list):
            k = ColorList(*k)

        if isinstance(k, ColorList):
            key = self.build_key(k)
            if key in self.map.keys():
                return self.map.__getitem__(key)

        try:
            key = str(k).lower()
            if k in self.map.keys():
                return self.map.__getitem__(k)

            for item in self.map.values():
                if item.name.lower() == key:
                    return item
                if key in [a.lower() for a in item.aliases]:
                    return item
        except TypeError:
            pass

        raise KeyError

    def __len__(self) -> int:
        return self.map.__len__()

    def __iter__(self) -> Iterator[str]:
        return self.map.__iter__()

    def build_key(self, colors: ColorList):
        return "".join([color.symbol for color in colors.unique().sort(self.pie)])


class Identity:
    def __init__(self, colors: ColorList):
        self.colors = colors.unique()
        self.name = str(self.colors)
        self.aliases = []
        self.edhrec = ""

    def describe(self, name: str = None, aliases: [str] = None, edhrec: str = None):
        if name:
            self.name = name
        if aliases:
            self.aliases.extend(aliases)
        if edhrec:
            self.edhrec = ""

    @property
    def is_multicolor(self):
        return len(self.colors) > 1


White = Color("W")
Blue = Color("U")
Black = Color("B")
Red = Color("R")
Green = Color("G")

ColorPie = Pie([White, Blue, Black, Red, Green])

ColorPie.identities[""].describe(
    "Colorless",
)
ColorPie.identities["W"].describe("Mono-White", ["White"])
ColorPie.identities["U"].describe("Mono-Blue", ["Blue"])
ColorPie.identities["B"].describe("Mono-Black", ["Black"])
ColorPie.identities["R"].describe("Mono-Red", ["Red"])
ColorPie.identities["G"].describe("Mono-Green", ["Green"])
ColorPie.identities["WU"].describe("Azorius", ["Azorius Senate"])
ColorPie.identities["WB"].describe("Orzhov", ["Orzhov Syndicate", "Silverquill"])
ColorPie.identities["WR"].describe("Boros", ["Boros Legion", "Lorehold"])
ColorPie.identities["WG"].describe("Selesnya", ["Selesnya Conclave"])
ColorPie.identities["UB"].describe("Dimir", ["House Dimir"])
ColorPie.identities["UR"].describe("Izzet", ["Izzet League", "Prismari"])
ColorPie.identities["UG"].describe("Simic", ["Simic Combine", "Quandrix"])
ColorPie.identities["BR"].describe("Rakdos", ["Cult of Rakdos"])
ColorPie.identities["BG"].describe("Golgari", ["Golgari Swarm", "Witherbloom"])
ColorPie.identities["RG"].describe("Gruul", ["Gruul Clans"])
ColorPie.identities["WUB"].describe("Esper", ["Obscura"])
ColorPie.identities["WUR"].describe("Jeskai", ["Jeskai Way", "Raugrin"])
ColorPie.identities["WUG"].describe("Bant", ["Brokers"])
ColorPie.identities["WBR"].describe("Mardu", ["Mardu Horde", "Savai"])
ColorPie.identities["WBG"].describe("Abzan", ["Abzan Houses", "Indatha"])
ColorPie.identities["WRG"].describe("Naya", ["Cabaretti"])
ColorPie.identities["UBR"].describe("Grixis", ["Maestros"])
ColorPie.identities["UBG"].describe("Sultai", ["Sultai Brood", "Zagoth"])
ColorPie.identities["URG"].describe("Temur", ["Temur Frontier", "Ketria"])
ColorPie.identities["BRG"].describe("Jund", ["Riveteers"])
ColorPie.identities["WUBR"].describe("Artifice", [""])
ColorPie.identities["WUBG"].describe("Growth", [""])
ColorPie.identities["WURG"].describe("Altruism", [""])
ColorPie.identities["WBRG"].describe("Aggression", [""])
ColorPie.identities["UBRG"].describe("Chaos", [""])
ColorPie.identities["WUBRG"].describe("WUBRG", ["5c", "Rainbow"])
