import json
import random
from typing import Dict, List, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character

with open('./data/items.json', 'r') as f:
    ITEM_DATA = json.loads(f.read())


class Item:
    """Contains utility functions for items, does not actually contain an item
    itself.

    An item is created using an internal name and a group of qualifiers, so a
    stick could be qualified with "oak" to make it an "oak" stick."""
    _item_data: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_item(cls, data: Dict[str, Any]):
        cls._item_data[data['id']] = data

    @staticmethod
    def get_display_name(item: Tuple[str, Dict[str, str]]) -> str:
        return Item.get_item_properties(item).get('name', 'Invalid Item')
    
    @staticmethod
    def get_description(item: Tuple[str, Dict[str, str]]) -> str:
        data = ITEM_DATA[item[0]]

        desc = data['description']['base']
        
        if 'extra' in data['description']:
            for k, v in data['description']['extra'].items():
                if Item.match_condition(item, k):
                    desc += '\n' + v

        return desc.format(
            **{k: v.capitalize() for k, v in item[1].items()}).strip()

    @staticmethod
    def get_item_properties(item: Tuple[str, Dict[str, str]]):
        data = ITEM_DATA[item[0]]
        return dict(
            name=data['name'].format(
                **{k: v.capitalize() for k, v in item[1].items()}).strip(),
            description=Item.get_description(item),
            internal_name=item[0],
            qualifiers=item[1],
            slots_taken=data['slots_taken'])
    
    @staticmethod
    def match_condition(item: Tuple[str, Dict[str, str]], condition: str) -> bool:
        """Checks if an item matches the condition provided.

        The conditions look like quality==excellent&&material==oak, which is
        compared to the qualifiers of the item.
        """
        qualifiers = item[1]
        for condition in condition.split('&&'):
            key, value = condition.split('==')
            if qualifiers.get(key) != value:
                return False
        return True
    
    @staticmethod
    async def handle_script(item: Tuple[str, Dict[str, str]], action: str, character: 'Character'):
        data = ITEM_DATA[item[0]]
        script: Dict[str, List[Any]] = data.get(action, None)
        if script:
            for k, v in script.items():
                if Item.match_condition(item, k):
                    await character.process_script(v)
                    return

    
    @staticmethod
    def get_sagewort_quality(*args, character: 'Character', **kwargs):
        herbalism_level = character.get_skill_level('herbalism')

        if herbalism_level < 1:
            return 'poor'
        elif herbalism_level < 6:
            return random.choice(['poor', 'poor', 'poor', 'average'])
        elif herbalism_level < 10:
            return random.choice(['poor', 'poor', 'average', 'average'])
        elif herbalism_level < 14:
            return random.choice(['poor', 'average', 'average', 'good'])
        elif herbalism_level < 18:
            return random.choice(['average', 'average', 'good', 'good'])
        elif herbalism_level < 22:
            return random.choice(['average', 'good', 'good', 'excellent'])
        
        return random.choice(['good', 'excellent', 'excellent'])
