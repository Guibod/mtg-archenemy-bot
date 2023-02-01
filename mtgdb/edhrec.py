import re
from typing import AsyncGenerator, Tuple, Optional

from aiohttp import ClientResponseError
from aiohttp_client_cache import CachedSession, SQLiteBackend

# https://json.edhrec.com/pages/commanders/year.json
# https://json.edhrec.com/pages/commanders/karazikar-the-eye-tyrant.json
# https://json.edhrec.com/cards/karazikar-the-eye-tyrant
#
# https://json.edhrec.com/pages/combos.json
# https://json.edhrec.com/pages/combos/w.json
# https://json.edhrec.com/pages/commanders/wubr.json
# https://json.edhrec.com/pages/backgrounds.json
#
# https://json.edhrec.com/pages/precon.json
# POST  https://edhrec.com/api/recs/
# content-type: application/json
# payload {"cards":["Sol ring","30x swamp","llanowar elves"],"commanders":["Viconia, Drow Apostate"],"name":""}
from aiostream import pipe, stream
import slugify

from mtgdb.ass import asyncio_run

salt_parser = re.compile(r"Salt Score: (?P<salt>[\d.]+)\n")
synergy_parser = re.compile(r"(?P<synergy>[\d.]+)% synergy")


class EdhRecError(Exception):
    def __init__(self, message, url=None, status=None):
        self.message=message
        self.url = url
        self.status = status

    def __str__(self):
        return "{message} (HTTP:{status} {url})".format(**self.__dict__)


class EdhRec:
    non_noise = ["name", "sanitized", "sanitized_wo", "cards", "url", "inclusion", "label", "num_decks", "count", "potential_decks", "salt_score", "synergy_score"]

    def __init__(self):
        self.root = "https://json.edhrec.com"
        self.session = CachedSession(cache=SQLiteBackend('._edhrec_cache'), expire_after=1000)

    @classmethod
    def sanitize(cls, string: Optional[str]):
        if string is None:
            return None
        return slugify.slugify(string, separator="-", replacements=[("'", ""), ("+", "plus-")])

    async def tribes(self) -> AsyncGenerator[dict, None]:
        async for (tag, item) in self.get_page("tribes.json", "tribes"):
            yield self._build(tag, item)

    async def tribes_by_color(self, color: str):
        color = self.sanitize(color)
        async for (tag, item) in self.get_related(f"commanders/{color}.json", "tribes"):
            yield self._build(tag, item)

    async def themes(self) -> AsyncGenerator[dict, None]:
        async for (tag, item) in self.get_page("themes.json", "themesbypopularitysort"):
            yield self._build(tag, item)

    async def themes_by_color(self, color: str):
        color = self.sanitize(color)
        async for (tag, item) in self.get_related(f"commanders/{color}.json", "themes"):
            yield self._build(tag, item)

    async def sets(self) -> AsyncGenerator[dict, None]:
        async for (tag, item) in self.get_page("sets.json", "sets"):
            yield self._build(tag, item)

    async def card_salt(self, year: str = None) -> AsyncGenerator[dict, None]:
        file = "top/salt.json"
        if year:
            file = f"top/salt-{year}.json"
        async for (tag, item) in self.get_page(file):
            yield self._build(tag, item)

    async def card_top_by_period(self, selector: str = "year") -> AsyncGenerator[dict, None]:
        if selector == "week":
            file = "top/week.json"
            tag = "pastweek"
        elif selector == "month":
            tag = "pastmonth"
        else:
            file = "top/year.json"
            tag = "past2years"
        async for (tag, item) in self.get_page(file, tag):
            yield self._build(tag, item)

    async def card_top_by_type(self, type: str, tag: str = "pastweek") -> AsyncGenerator[dict, None]:
        type = self.sanitize(type)
        tag = self.sanitize(tag)
        file = f"top/{type}.json"
        async for (tag, item) in self.get_page(file, tag):
            yield self._build(tag, item)

    async def card_by_theme(self, theme, selector: str = None, tag: str = None):
        theme = self.sanitize(theme)
        selector = self.sanitize(selector)
        file = f"themes/{theme}.json"
        if selector:
            file = f"themes/{theme}/{selector}.json"
        async for (tag, item) in self.get_page(file, tag):
            yield self._build(tag, item)

    async def card_by_set(self, code: str, tag: str = None) -> AsyncGenerator[dict, None]:
        code = self.sanitize(code)
        tag = self.sanitize(tag)
        async for (tag, item) in self.get_page(f"sets/{code}.json", tag):
            yield self._build(tag, item)

    async def companions(self) -> AsyncGenerator[dict, None]:
        async for (tag, item) in self.get_page("companions.json", "companions"):
            yield self._build(tag, item)

    async def partners(self, selector: str = None) -> AsyncGenerator[dict, None]:
        selector = self.sanitize(selector)
        file = "partners.json"
        if selector:
            file = "partners/{}.json".format(selector)
        async for (tag, item) in self.get_page(file):
            yield self._build(tag, item)

    async def commanders(self, selector: str = None) -> AsyncGenerator[dict, None]:
        selector = self.sanitize(selector)
        file = "commanders.json"
        if selector:
            file = f"commanders/{selector}.json"
        async for (tag, item) in self.get_page(file):
            yield self._build(tag, item)

    async def commander(self, slug: str, tag: str = None) -> AsyncGenerator[dict, None]:
        slug = self.sanitize(slug)
        tag = self.sanitize(tag)
        async for (tag, item) in self.get_page(f"commanders/{slug}.json", tag):
            yield self._build(tag, item)

    async def combos_by_color(self, color: str) -> AsyncGenerator[dict, None]:
        color = self.sanitize(color)
        async for (tag, item) in self.get_page(f"commanders/{color}.json"):
            yield self._build(tag, item)

    def _build(self, tag, item):
        body = {"tag": tag}
        for key in self.non_noise:
            if key in item.keys():
                body[key] = item[key]

        # TODO: sanitize don’t work on themes, see zombie token__S__
        body["slug"] = self.sanitize(body.get("name", ""))

        salt = salt_parser.search(item.get("label", ""))
        if salt:
            body["salt_score"] = float(salt.group("salt"))

        synergy = synergy_parser.search(item.get("label", ""))
        if synergy:
            body["synergy_score"] = float(synergy.group("synergy"))

        return body

    async def get_related(self, file, tag) -> AsyncGenerator[Tuple[str, dict], None]:
        url = f'{self.root}/pages/{file}'
        try:
            async with self.session:
                async with self.session.get(url) as f:
                    f.raise_for_status()
                    data = await f.json()

                    for info in data.get("relatedinfo", {}).get(tag, []):
                        yield tag, info
        except ClientResponseError as e:
            raise EdhRecError(message="Failed to fetch data from EDHREC", url=e.request_info.real_url, status=e.status)

    async def get_page(self, file, tag=None) -> AsyncGenerator[Tuple[str, dict], None]:
        url = f'{self.root}/pages/{file}'
        try:
            async with self.session:
                async with self.session.get(url) as f:
                    f.raise_for_status()
                    data = await f.json()

                    for card_list in data.get("container", {}).get("json_dict", {}).get("cardlists"):
                        current_tag = card_list.get("tag", "")
                        if tag is not None and tag != current_tag:
                            continue

                        for item in card_list.get("cardviews", []):
                            yield current_tag, item

                        while card_list.get("more"):
                            url = "{root}/pages/{file}".format(root=self.root, file=card_list.get("more"))
                            async with self.session.get(url) as f:
                                card_list = await f.json()
                                for item in card_list.get("cardviews", []):
                                    yield current_tag, item
        except ClientResponseError as e:
            raise EdhRecError(message="Failed to fetch data from EDHREC", url=e.request_info.real_url, status=e.status)


if __name__ == '__main__':
    async def main():
        rec = EdhRec()
        s = stream.preserve(rec.themes()) | pipe.print()
        # s = stream.preserve(rec.card_top_by_type("enchantments")) | pipe.print()
        # s = stream.preserve(rec.tribes_by_color("ub")) | pipe.print()
        # s = stream.preserve(rec.themes_by_color("ub")) | pipe.print()
        # s = stream.preserve(rec.commanders("ub")) | pipe.print()
        # s = stream.preserve(rec.commander("gyruda-doom-of-depths")) | pipe.print()
            # | pipe.filter(lambda x: x["sanitized"] != x["slug"])\
        await s

    asyncio_run(main())