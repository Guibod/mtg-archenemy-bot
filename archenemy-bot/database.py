import os.path
from datetime import timedelta
from itertools import groupby

from mtgtools import PCardList
from mtgtools.MtgDB import MtgDB
from requests_cache import CachedSession
from BTrees.OOBTree import BTree

class Database:
    cards: PCardList

    def __init__(self, file):
        self.db = MtgDB(file)
        self.cards = self.db.root.scryfall_cards
        self.session = CachedSession(
            'mtg_database',
            expire_after=timedelta(days=1)
        )

    def update(self, init=True, verbose=True):
        if init:
            self.db.scryfall_bulk_update(bulk_type="oracle_cards", verbose=verbose)
        else:
            self.db.scryfall_update(verbose=verbose)

        self.db.root.idx_id = self.cards.create_id_index()
        self.db.root.idx_oracle_id = self.create_oracle_id_index()
        self.db.commit()

    def load_tags(self):
        url = "https://api.scryfall.com/private/tags/oracle?pretty=true"
        response = self.session.get(url=url)
        data = response.json()
        for tag in response.json().get("data"):
            label = tag.get("label")
            for oracle_id in tag.get("oracle_ids", []):
                print(self.db.root.idx_oracle_id[oracle_id])
                # print(self.cards.where(oracle_id=oracle_id))

    def create_oracle_id_index(self):
        sorted_cards = self.cards.sorted(lambda card: card.oracle_id)
        return BTree(dict((k, list(v)) for k, v in groupby(sorted_cards, key=lambda card: card.oracle_id)))



if __name__ == '__main__':
    db = Database(os.path.expanduser("~/mtg.db"))
    db.update()
    db.load_tags()