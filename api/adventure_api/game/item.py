import json
from typing import Dict, Tuple

with open('./data/items.json', 'r') as f:
    ITEM_DATA = json.loads(f.read())


class Item:
    """Contains utility functions for items, does not actually contain an item
    itself.

    An item is created using an internal name and a group of qualifiers, so a
    stick could be qualified with "oak" to make it an "oak" stick."""

    @staticmethod
    def get_display_name(item: Tuple[str, Dict[str, str]]):
        return Item.get_item_properties(item).get('name', 'Invalid Item')

    @staticmethod
    def get_item_properties(item: Tuple[str, Dict[str, str]]):
        data = ITEM_DATA[item[0]]
        return dict(
            name=data['name'].format(
                **{k: v.capitalize() for k, v in item[1].items()}).strip(),
            internal_name=item[0],
            qualifiers=item[1],
            slots_taken=data['slots_taken'])
