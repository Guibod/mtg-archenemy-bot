import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Generator
from uuid import UUID, uuid4

import ijson
from aiohttp_client_cache import CachedSession, SQLiteBackend
from beanie import Document
from pydantic import AnyUrl, Field
from typing_extensions import TypedDict


class Color(str):
    WHITE="W"
    BLUE="U"
    BLACK="B"
    RED="R"
    GREEN="G"
    COLORLESS="C"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            # simplified regex here for brevity, see the wikipedia link above
            pattern='^[WUBRG]$',
            # some example postcodes
            examples=['U', 'W'],
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        if v not in [cls.WHITE, cls.BLUE, cls.BLACK, cls.RED, cls.GREEN, cls.COLORLESS]:
            raise TypeError('string is not a legal color code')

    def __repr__(self):
        return f'Color({super().__repr__()})'


class RelatedObject(TypedDict, total=False):
    id: UUID
    object: str
    """A content type for this object, always related_card."""
    component: str
    """A field explaining what role this card plays in this relationship, one of:
     token, meld_part, meld_result, or combo_piece."""
    name: str
    """The name of this particular related card."""
    type_line: str
    """The type line of this card."""
    uri: AnyUrl
    """A URI where you can retrieve a full object describing this card on Scryfall’s API."""


class CardImagery(TypedDict, total=False):
    png: Optional[AnyUrl]
    """A transparent, rounded full card PNG. This is the best image to use for videos or other high-quality content."""
    border_crop: Optional[AnyUrl]
    """A full card image with the rounded corners and the majority of the border cropped off. 
    Designed for dated contexts where rounded images can’t be used."""
    art_crop: Optional[AnyUrl]
    """A rectangular crop of the card’s art only. Not guaranteed to be perfect for cards 
    with outlier designs or strange frame arrangements"""
    large: Optional[AnyUrl]
    """A large full card image"""
    normal: Optional[AnyUrl]
    """A medium-sized full card image"""
    small: Optional[AnyUrl]
    """A small full card image. Designed for use as thumbnail or list icon."""


class CardFace(TypedDict, total=False):
    artist: Optional[str]
    """The name of the illustrator of this card face. Newly spoiled cards may not have this field yet."""
    cmc: Optional[Decimal]
    """The mana value of this particular face, if the card is reversible."""
    color_indicator: Optional[List[Color]]
    """The colors in this face’s color indicator, if any."""
    colors: Optional[List[Color]]
    """This face’s colors, if the game defines colors for the individual face of this card."""
    flavor_text: Optional[str]
    """The flavor text printed on this face, if any."""
    illustration_id: Optional[UUID]
    """A unique identifier for the card face artwork that remains consistent across reprints. 
    Newly spoiled cards may not have this field yet."""
    image_uris: Optional[CardImagery]
    """An object providing URIs to imagery for this face, if this is a double-sided card. 
    If this card is not double-sided, then the image_uris property will be part of the parent object instead."""
    layout: Optional[str]
    """The layout of this card face, if the card is reversible."""
    loyalty: Optional[str]
    """This face’s loyalty, if any."""
    mana_cost: str
    """The mana cost for this face. This value will be any empty string
    if the cost is absent. Remember that per the game rules, a missing mana cost and a mana cost of {0} are different values."""
    name: str
    object: str
    """A content type for this object, always card_face."""
    oracle_id: Optional[UUID]
    """The Oracle ID of this particular face, if the card is reversible."""
    oracle_text: Optional[str]
    """The Oracle text for this face, if any."""
    power: Optional[str]
    """This face’s power, if any. Note that some cards have powers that are not numeric, such as *."""
    printed_name: Optional[str]
    """The localized name printed on this face, if any."""
    printed_text: Optional[str]
    """The localized text printed on this face, if any."""
    printed_type_line: Optional[str]
    """The localized type line printed on this face, if any."""
    toughness: Optional[str]
    """This face’s toughness, if any."""
    type_line: Optional[str]
    """The type line of this particular face, if the card is reversible."""
    watermark: Optional[str]
    """The watermark on this particulary card face, if any."""


class Preview(TypedDict, total=False):
    previewed_at: Optional[datetime.date]
    """The date this card was previewed"""
    source_uri: Optional[str]
    """A link to the preview for this card."""
    source: Optional[str]
    """The name of the source that previewed this card."""


class Tag(Document):
    object: str
    id: UUID = Field(default_factory=uuid4)
    label: str
    type: str
    description: Optional[str]
    oracle_ids: List[UUID]

    class Settings:
        name = "tags"


class Card(Document):
    arena_id: Optional[int] = None
    """This card’s Arena ID, if any. A large percentage of cards are not available on Arena and do not have this ID."""

    id: UUID = Field(default_factory=uuid4)
    """A unique ID for this card in Scryfall’s database."""
    lang: str
    """A language code for this printing."""
    mtgo_id: Optional[int]
    """This card’s Magic Online ID (also known as the Catalog ID), if any. 
    A large percentage of cards are not available on Magic Online and do not have this ID."""
    mtgo_foil_id: Optional[int]
    """This card’s foil Magic Online ID (also known as the Catalog ID), if any.
    A large percentage of cards are not available on Magic Online and do not have this ID."""
    multiverse_ids: Optional[List[int]]
    """This card’s multiverse IDs on Gatherer, if any, as an array of integers. 
    Note that Scryfall includes many promo cards, tokens, and other esoteric objects that do not have these identifiers."""
    tcgplayer_id: Optional[int]
    """This card’s ID on TCGplayer’s API, also known as the productId."""
    tcgplayer_etched_id: Optional[int]
    """This card’s ID on TCGplayer’s API, for its etched version if that version is a separate product."""
    cardmarket_id: Optional[int]
    """This card’s ID on Cardmarket’s API, also known as the idProduct."""
    object: str
    """A content type for this object, always card."""
    oracle_id: UUID
    """A unique ID for this card’s oracle identity. 
    This value is consistent across reprinted card editions, and unique among different cards with the same name (tokens, Unstable variants, etc)."""
    prints_search_uri: str
    """A link to where you can begin paginating all re/prints for this card on Scryfall’s API."""
    rulings_uri: AnyUrl
    """A link to this card’s rulings list on Scryfall’s API."""
    scryfall_uri: AnyUrl
    """A link to this card’s permapage on Scryfall’s website."""
    uri: AnyUrl
    """A link to this card object on Scryfall’s API."""

    all_parts: Optional[List[dict]]
    """If this card is closely related to other cards, this property will be an array with Related Card Objects."""
    card_faces: Optional[List[dict]]
    """An array of Card Face objects, if this card is multifaced."""
    cmc: Decimal
    """The card’s converted mana cost. Note that some funny cards have fractional mana costs."""
    color_identity: List[Color]
    """This card’s color identity."""
    color_indicator: Optional[List[Color]]
    """The colors in this card’s color indicator, if any. 
    A null value for this field indicates the card does not have one."""
    colors: Optional[List[Color]]
    """This card’s colors, if the overall card has colors defined by the rules. 
    Otherwise the colors will be on the card_faces objects, see below."""
    edhrec_rank: Optional[int]
    """This card’s overall rank/popularity on EDHREC. Not all cards are ranked."""
    hand_modifier: Optional[str]
    """This card’s hand modifier, if it is Vanguard card. This value will contain a delta, such as -1."""
    keywords: List[str]
    """An array of keywords that this card uses, such as 'Flying' and 'Cumulative upkeep'."""
    layout: str
    """A code for this card’s layout."""
    legalities: dict
    """An object describing the legality of this card across play formats. 
    Possible legalities are legal, not_legal, restricted, and banned."""
    life_modifier: Optional[str]
    """This card’s life modifier, if it is Vanguard card. This value will contain a delta, such as +2."""
    loyalty: Optional[str]
    """This loyalty if any. Note that some cards have loyalties that are not numeric, such as X."""
    mana_cost: Optional[str]
    """The mana cost for this card. This value will be any empty string "" if the cost is absent. 
    Remember that per the game rules, a missing mana cost and a mana cost of {0} are different values. 
    Multi-faced cards will report this value in card faces."""
    name: str
    """The name of this card. If this card has multiple faces, this field will contain both names separated by ␣//␣."""
    oracle_text: Optional[str]
    """The Oracle text for this card, if any."""
    oversized: bool
    """True if this card is oversized."""
    penny_rank: Optional[int]
    """This card’s rank/popularity on Penny Dreadful. Not all cards are ranked."""
    power: Optional[str]
    """This card’s power, if any. Note that some cards have powers that are not numeric, such as *."""
    produced_mana: Optional[List[str]]
    """Colors of mana that this card could produce."""
    reserved: bool
    """True if this card is on the Reserved List."""
    toughness: Optional[str]
    """This card’s toughness, if any. Note that some cards have toughnesses that are not numeric, such as *."""
    type_line: str
    """The type line of this card."""

    artist: Optional[str]
    """The name of the illustrator of this card. Newly spoiled cards may not have this field yet."""
    attraction_lights: Optional[List[str]]
    """The lit Unfinity attractions lights on this card, if any."""
    booster: bool
    """Whether this card is found in boosters."""
    border_color: str
    """This card’s border color: black, white, borderless, silver, or gold."""
    card_back_id: Optional[UUID]
    """The Scryfall ID for the card back design present on this card."""
    collector_number: str
    """This card’s collector number. Note that collector numbers can contain non-numeric characters, 
    such as letters or ★."""
    content_warning: Optional[bool]
    """True if you should consider avoiding use of this print downstream."""
    digital: bool
    """	True if this card was only released in a video game."""
    finishes: List[str]
    """An array of computer-readable flags that indicate if this card can come in foil, nonfoil, or etched finishes."""
    flavor_name: Optional[str]
    """The just-for-fun name printed on the card (such as for Godzilla series cards)."""
    flavor_text: Optional[str]
    """The flavor text, if any."""
    frame_effects: Optional[List[str]]
    """This card’s frame effects, if any."""
    frame: str
    """This card’s frame layout."""
    full_art: bool
    """True if this card’s artwork is larger than normal."""
    games: List[str]
    """A list of games that this card print is available in, paper, arena, and/or mtgo."""
    highres_image: bool
    """True if this card’s imagery is high resolution."""
    illustration_id: Optional[UUID]
    """A unique identifier for the card artwork that remains consistent across reprints. 
    Newly spoiled cards may not have this field yet."""
    image_status: str
    """A computer-readable indicator for the state of this card’s image, one of :
    missing, placeholder, lowres, or highres_scan."""
    image_uris: Optional[CardImagery]
    """An object listing available imagery for this card. See the Card Imagery article for more information."""
    prices: Dict[str, Optional[str]]
    """An object containing daily price information for this card, including:
     usd, usd_foil, usd_etched, eur, and tix prices, as strings."""
    printed_name: Optional[str]
    """The localized name printed on this card, if any."""
    printed_text: Optional[str]
    """The localized text printed on this card, if any."""
    printed_type_line: Optional[str]
    """The localized type line printed on this card, if any."""
    promo: bool
    """True if this card is a promotional print."""
    promo_types: Optional[List[str]]
    """An array of strings describing what categories of promo cards this card falls into."""
    purchase_uris: Optional[Dict[str, str]]
    """An object providing URIs to this card’s listing on major marketplaces."""
    rarity: str
    """This card’s rarity. One of common, uncommon, rare, special, mythic, or bonus."""
    related_uris: Dict[str, AnyUrl]
    """An object providing URIs to this card’s listing on other Magic: The Gathering online resources."""
    released_at: datetime.date
    """The date this card was first released."""
    reprint: bool
    """True if this card is a reprint."""
    scryfall_set_uri: AnyUrl
    """A link to this card’s set on Scryfall’s website."""
    set_name: str
    """This card’s full set name."""
    set_search_uri: AnyUrl
    """A link to where you can begin paginating this card’s set on the Scryfall API."""
    set_type: str
    """The type of set this printing is in."""
    set_uri: AnyUrl
    """A link to this card’s set object on Scryfall’s API."""
    set_code: str = Field(alias="set")
    """This card’s set code."""
    set_id: UUID
    """This card’s Set object UUID."""
    story_spotlight: bool
    """True if this card is a Story Spotlight."""
    textless: bool
    """True if the card is printed without text."""
    variation: bool
    """Whether this card is a variation of another printing."""
    variation_of: Optional[UUID]
    """The printing ID of the printing this card is a variation of."""
    security_stamp: Optional[str]
    """The security stamp on this card, if any. One of oval, triangle, acorn, circle, arena, or heart."""
    watermark: Optional[str]
    """This card’s watermark, if any."""
    preview: Optional[Preview]

    class Settings:
        name = "cards"
        bson_encoders = {
            datetime.date: lambda dt: datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0,
                                                        second=0)
        }


class Scryfall:
    def __init__(self):
        self.root = "https://api.scryfall.com"
        self.session = CachedSession(cache=SQLiteBackend('._scryfall_cache'), expire_after=1000)

    async def get_bulk_tags(self, tag_type: str) -> Generator[dict, None, None]:
        url = "{root}/private/tags/{type}".format(root=self.root, type=tag_type)
        async with self.session:
            async with self.session.get(url) as f:
                async for current_tag in ijson.items_async(f.content, 'data.item'):
                    yield current_tag

    async def get_bulk_data(self, bulk_type: str) -> Generator[dict, None, None]:
        url = '{root}/bulk-data/'.format(root=self.root)
        bulk_types = []
        bulk = None
        async with self.session:
            async with self.session.get(url) as f:
                async for current_bulk in ijson.items_async(f.content, 'data.item'):
                    bulk_types.append(current_bulk.get("type"))
                    if current_bulk.get("type") == bulk_type:
                        bulk = current_bulk

            if not bulk:
                raise IndexError("{} bulk type not found in {}", bulk_type, ",".join(bulk_types))

            async with self.session.get(bulk.get("download_uri")) as f:
                async for current_card in ijson.items_async(f.content, 'item'):
                    yield current_card