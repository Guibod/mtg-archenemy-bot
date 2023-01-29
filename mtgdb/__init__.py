import asyncio
from typing import Optional

from aiostream import stream, pipe

from motor.motor_asyncio import AsyncIOMotorClient

from beanie import Document, init_beanie

from mtgdb.scryfall import Tag, Card, Scryfall


class DB:
    def __init__(self, client):
        self.client = client
        self.scryfall = Scryfall()

    async def init(self):
        await init_beanie(database=self.client.db_name, document_models=[Card, Tag])

    async def load(self, limit=None):
        async def write(item: Document):
            await item.save()

        def do_limit(stream, limit: Optional[int]):
            if limit:
                stream |= pipe.take(limit)
            return stream

        await Tag.delete_all()
        await Card.delete_all()

        s1 = do_limit(stream.preserve(self.scryfall.get_bulk_tags("oracle")), limit) | pipe.map(lambda x: Tag.parse_obj(x))
        s2 = do_limit(stream.preserve(self.scryfall.get_bulk_data("oracle_cards")), limit) | pipe.map(lambda x: Card.parse_obj(x))
        # s3 = do_limit(stream.preserve(self.scryfall.get_bulk_tags("illustration")), limit) | pipe.map(lambda x: Tag.parse_obj(x))

        s = stream.merge(s1, s2) | pipe.action(write)

        await s



async def main():
    client = AsyncIOMotorClient("mongodb://admin:password@localhost:37017/mtg?authSource=admin")
    db = DB(client)
    await db.init()
    await db.load(20000)

if __name__ == '__main__':
    asyncio.run(main())
