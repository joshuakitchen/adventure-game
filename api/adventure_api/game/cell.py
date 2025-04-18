import asyncio
import json
import random
from .enemy import Enemy
from .item import Item
from noise import snoise2
from typing import Any, Callable, Dict, Optional, List, NamedTuple, Tuple, Union, TYPE_CHECKING


if TYPE_CHECKING:
    from .character import Character

HEIGHT_SCALE = 60
TREE_SCALE = 30

with open('./data/biomes.json', 'r') as f:
    BIOME_DATA: Dict[str, Any] = json.loads(f.read())

MAX_ENEMIES = 4
SPAWN_TICK = 60


class Cell:
    """A cell is a location in the game which contains many things, a cell
    should cover a wide area such as a forest or village but villages and
    forests which cover multiple cells should be captured in the description."""
    _x: int
    _z: int
    _biome: str
    _claimed_by: Optional[str]
    _characters: List['Character']
    _enemies: List[Enemy]
    _items: List[Tuple[str, Dict[str, str]]]
    _spawn_tick: int

    def __init__(self, x: int, z: int):
        self._x = x
        self._z = z
        self._characters = []
        self._enemies = []
        self._items = [
            ['dead_rabbit', {}],
        ]
        self._claimed_by = None
        self._spawn_tick = SPAWN_TICK
        self.load()
        for _ in range(MAX_ENEMIES):
            self.spawn_random_enemy()
            if random.random() > 0.5:
                break

    async def tick(self):
        if self._spawn_tick > 0:
            self._spawn_tick = self._spawn_tick - 1
        for c in self._characters:
            await c.tick()
        for e in self._enemies:
            await e.tick()
        if len(self._enemies) < MAX_ENEMIES and self._spawn_tick == 0:
            if random.random() > 0.7:
                e = self.spawn_random_enemy()
                if isinstance(e.data['on_entry'], Callable):
                    await e.data['on_entry'](e, self)
                else:
                    await self.send_message(
                        'game', '@red@{}@res@ is wandering nearby.', e.name)
            self._spawn_tick = SPAWN_TICK
    
    def spawn_random_enemy(self) -> Enemy:
        if 'enemies' in self.data:
            max_chance = sum([e[1] for e in self.data['enemies']])
            rand = random.random() * max_chance

            for enemy in self.data['enemies']:
                rand -= enemy[1]
                if rand <= 0:
                    return self.spawn(enemy[0])

    async def send_message(self, type: str, message: str, *args, **kwargs):
        await asyncio.gather(*[
            c.send_message(type, message, *args, **kwargs)
            for c in self._characters
        ])

    def load(self):
        self.generate()

    def generate(self):
        height = snoise2(
            self._x / HEIGHT_SCALE,
            self._z / HEIGHT_SCALE,
            octaves=6,
            lacunarity=2,
            persistence=0.5) * 100 + 30
        trees = snoise2(
            (self._x + 1000) / TREE_SCALE,
            (self._z + 1000) / TREE_SCALE,
            octaves=4,
            lacunarity=2,
            persistence=0.5
        ) * 100
        if height < 0:
            self._biome = 'sea'
        elif height > 60:
            self._biome = 'mountain'
        else:
            if trees > 0:
                self._biome = 'forest'
            else:
                self._biome = 'plains'

    def add_item(self, item: Tuple[str, Dict[str, str]]):
        self._items.append(item)

    @property
    def biome_icon(self):
        if self._biome == 'forest':
            return '\x1b[32m"\uFE0E\x1b[0m'
        elif self._biome == 'mountain':
            return '\x1b[90m^\x1b[0m'
        elif self._biome == 'plains':
            return '\x1b[32m.\x1b[0m'
        return '\x1b[34m~\x1b[0m'

    @property
    def population_icon(self):
        if len(self._characters) >= 20:
            return '█'
        elif len(self._characters) >= 10:
            return '▓'
        elif len(self._characters) >= 5:
            return '▒'
        elif len(self._characters) >= 1:
            return '░'
        return '.'

    def get_scavenge_item(self) -> Optional[Tuple[str, Dict[str, str]]]:
        scavenge_list = self._get_scavenge_list()
        if scavenge_list is None:
            return None
        item = random.choice(scavenge_list)
        return [item[0], item[1]]

    def _get_scavenge_list(self) -> Optional[List[Tuple[str, Dict[str, str]]]]:
        """Generates the list of items that can be scavenged."""
        if self._biome not in BIOME_DATA:
            return None
        return BIOME_DATA[self._biome]['scavenge']

    def get(self, target_id: str) -> Optional[Union[Enemy, 'Character']]:
        if target_id[-2:] == '00':
            return next(
                iter(
                    [e for e in self._characters
                     if e._instance_id == target_id]))
        elif target_id[-2:] == '01':
            return next(
                iter(
                    [e for e in self._enemies
                     if e.id == target_id and not e.is_dead]),
                None)
        return None

    def find(self, target: str) -> List[Enemy]:
        """Attempts to find a target within the current cell, this can return
        multiple targets which should then be reduced with an ordinal.

        This should handle external names and convert them to internal names
        too."""
        targets: List[Enemy] = []
        for e in self._enemies:
            if e.name.lower() == target.lower():
                targets.append(e)
        return targets

    def spawn(self, enemy: str) -> Enemy:
        """Spawns an enemy within the Cell."""
        e = Enemy(self, enemy)
        self._enemies.append(e)
        return e

    def remove(self, e: Enemy):
        self._enemies.remove(e)

    @property
    def description(self) -> str:
        desc = self.data.get('description', {'base': []})
        base = desc.get('base', [])

        rng = random.Random((self._x << 16) + self._z)
        return rng.choice(base)

    @property
    def can_scavenge(self) -> bool:
        return self._get_scavenge_list is not None

    @property
    def entities(self) -> List[Union['Character',Enemy]]:
        return self._characters + self._enemies

    @property
    def characters(self) -> List['Character']:
        return self._characters

    @property
    def enemies(self) -> List[Enemy]:
        return self._enemies
    
    @property
    def items(self) -> List[str]:
        return [Item.get_item_properties(item) for item in self._items]

    @property
    def data(self) -> Dict[str, Any]:
        return BIOME_DATA.get(self._biome, {})
