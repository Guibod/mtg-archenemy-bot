import itertools
import logging
from collections import Counter
from typing import Union, Mapping, Iterator, Sequence, Iterable

# TODO: Introduce CMC (phyrexian, hybrid)
# TODO: Maybe wacky color and values from unsets
from ordered_set import OrderedSet

logger = logging.getLogger(__name__)


class Color:
    def __init__(self, symbol):
        self.symbol: str = symbol

    def __str__(self):
        return f"{{{self.symbol.upper()}}}"

    def __repr__(self):
        return f"Color({self.symbol})"


class ColorPie(Sequence[Color]):
    def __init__(self, *args: [Color]):
        self.colors = self.sanitize(args)

    @classmethod
    def sanitize(cls, colors: Iterable[Color]) -> [Color]:
        if not all(isinstance(x, Color) for x in colors):
            raise ValueError("Please provide a Color object iterable")
        duplicates = [k for k, v in Counter(list(colors)).items() if v > 1]
        if len(duplicates):
            raise ValueError("A color pie cannot hold the same color twice. {}".format(",".join(map(str, duplicates))))
        # TODO: search duplicates color values
        return list(colors)

    def __getitem__(self, i: Union[int, str]):
        if isinstance(i, int):
            return self.colors[i]

        try:
            return next(color for color in self.colors if color.symbol == i)
        except StopIteration:
            raise KeyError(f"{i} not found in {self}")

    def __len__(self) -> int:
        return len(self.colors)

    def __iter__(self) -> Iterator[Color]:
        return iter(self.colors)

    def shift(self, color: Color, step: int = 1) -> Color:
        return self.colors[(step + self.index(color)) % len(self.colors)]

    def __hash__(self):
        return hash(tuple(self))

    def parse(self, identity_as_string: str) -> "Identity":
        colors = []
        for letter in identity_as_string:
            colors.append(self.__getitem__(letter))
        return Identity(self, colors)

    def combinations(self):
        """
        A mathematical computation of all possible combinations of colors
        This will not provide a proper color pie centric combination though and cannot be used to
        provide a complete identity map that would build the red enemy guild (Boros) as rw,
        instead of wr in this case

        :return:
        """
        return [Identity(self, c)
                for length in range(0, len(self.colors) + 1)
                for c in itertools.combinations(self.colors, length)]

    def build_identity_map(self) -> "IdentityMap":
        idmap = IdentityMap(self)
        logger.debug("Start color-pie combinations")
        idmap.add(Identity(self, []))
        logger.debug("Already added colorless")

        t = len(self.colors)
        for n in range(0, t + 1):
            logger.debug(f"{' ' * 2}- building a list of {n} color(s)")
            for step in range(1, n + 1):
                logger.debug(f"{' ' * 4}- With step: {step} (0=same 1=allied, 2=enemy, 3+=!?)")
                if t % step == 0 and t / step < n:
                    logger.debug(f"{' ' * 6}- This strategy cannot be fulfilled and will result a loop")
                    continue

                for color in self.colors:
                    logger.debug(f"{' ' * 6}- With color: {color}")
                    colors = [color]
                    i = 0
                    while i < n - 1:
                        picked_color = self.shift(colors[-1], step)
                        logger.debug(f"{' ' * 8}- Picking color {i}: {picked_color}")
                        colors.append(picked_color)
                        i += 1

                    ident = Identity(self, colors)
                    logger.debug(f"{' ' * 6}- added {ident}")
                    idmap.add(ident)

        return idmap

    def __repr__(self):
        return f"ColorPie({self.colors})"


class Identity(Sequence[Color]):
    def __init__(self, pie: ColorPie, colors: Iterable[Color]):
        self.pie = pie
        self.colors = OrderedSet(colors)
        self._name = None
        self.aliases = []

    def describe(self, name: str = None, aliases: [str] = None):
        if name:
            self._name = name
        if aliases:
            self.aliases.extend(aliases)

    @property
    def name(self):
        if not self._name:
            return self.canonical
        return self._name

    @property
    def canonical(self) -> str:
        if len(self.colors) == 0:
            return "colorless"
        return "".join([color.symbol for color in self.colors])

    def checksum(self) -> int:
        """ Checksum is computed from binary position of the color in the color-pie"""
        return sum([1 << self.pie.index(color) for color in self.colors])

    def matches(self, k: str):
        search = k.lower()
        if search in self.name.lower():
            return True
        if search in map(lambda x: x.lower(), self.aliases):
            return True
        return False

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"Identity({self.canonical})"

    def __getitem__(self, i: int) -> Color:
        return self.colors.__getitem__(i)

    def __len__(self):
        return len(self.colors)

    def __eq__(self, other: "Identity"):
        try:
            return other.checksum() == self.checksum()
        except TypeError:
            return False


class IdentityMap(Mapping[int, Identity]):
    def __init__(self, pie: ColorPie):
        self.map = dict()
        self.pie = pie

    def add(self, ident: Identity):
        if ident.checksum() not in self.map:
            self.map[ident.checksum()] = ident

    def __getitem__(self, k: Union[int, str, Identity]) -> Identity:
        if isinstance(k, int):
            return self.map[k]

        if isinstance(k, Identity):
            return self.map[k.checksum()]

        if not isinstance(k, str):
            raise KeyError

        try:
            match = self.pie.parse(k)
            return self.map[match.checksum()]
        except KeyError:
            for identity in self.map.values():
                if identity.matches(k):
                    return identity

        raise KeyError

    def __len__(self) -> int:
        return self.map.__len__()

    def __iter__(self) -> Iterator[str]:
        return self.map.__iter__()


White = Color("w")
Blue  = Color("u")
Black = Color("b")
Red   = Color("r")
Green = Color("g")

MagicColorPie = ColorPie(White, Blue, Black, Red, Green)
MagicIdentities = MagicColorPie.build_identity_map()
MagicIdentities[""].describe("Colorless")
MagicIdentities["w"].describe("Mono-White", ["White"])
MagicIdentities["u"].describe("Mono-Blue", ["Blue"])
MagicIdentities["b"].describe("Mono-Black", ["Black"])
MagicIdentities["r"].describe("Mono-Red", ["Red"])
MagicIdentities["g"].describe("Mono-Green", ["Green"])
MagicIdentities["wu"].describe("Azorius", ["Azorius Senate"])
MagicIdentities["ub"].describe("Dimir", ["House Dimir"])
MagicIdentities["br"].describe("Rakdos", ["Cult of Rakdos"])
MagicIdentities["rg"].describe("Gruul", ["Gruul Clans"])
MagicIdentities["gu"].describe("Simic", ["Simic Combine", "Quandrix"])
MagicIdentities["gw"].describe("Selesnya", ["Selesnya Conclave"])
MagicIdentities["wb"].describe("Orzhov", ["Orzhov Syndicate", "Silverquill"])
MagicIdentities["ur"].describe("Izzet", ["Izzet League", "Prismari"])
MagicIdentities["rw"].describe("Boros", ["Boros Legion", "Lorehold"])
MagicIdentities["gb"].describe("Golgari", ["Golgari Swarm", "Witherbloom"])
MagicIdentities["wub"].describe("Esper", ["Obscura"])
MagicIdentities["ubr"].describe("Grixis", ["Maestros"])
MagicIdentities["brg"].describe("Jund", ["Riveteers"])
MagicIdentities["rgw"].describe("Naya", ["Cabaretti"])
MagicIdentities["guw"].describe("Bant", ["Brokers"])
MagicIdentities["wbg"].describe("Abzan", ["Abzan Houses", "Indatha"])
MagicIdentities["urw"].describe("Jeskai", ["Jeskai Way", "Raugrin"])
MagicIdentities["bgu"].describe("Sultai", ["Sultai Brood", "Zagoth"])
MagicIdentities["rwb"].describe("Mardu", ["Mardu Horde", "Savai"])
MagicIdentities["gur"].describe("Temur", ["Temur Frontier", "Ketria"])
MagicIdentities["wubr"].describe("Artifice", ["Yore-Tiller", "Green-less", "Yore"])
MagicIdentities["ubrg"].describe("Chaos", ["Glint-Eye", "White-less", "Glint"])
MagicIdentities["brgw"].describe("Aggression", ["Dune-Brood", "Blue-less", "Dune"])
MagicIdentities["rgwu"].describe("Altruism", ["Ink-Treader", "Black-less", "Ink"])
MagicIdentities["gwub"].describe("Growth", ["Witch-Maw", "Red-less", "Witch"])
MagicIdentities["wubrg"].describe("Five-Color", ["5c", "Rainbow"])
