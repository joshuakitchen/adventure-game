import json
import random
from noise import snoise2
from typing import Any, Dict, Optional, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character

HEIGHT_SCALE = 60
TREE_SCALE = 30

with open('./data/biomes.json', 'r') as f:
    BIOME_DATA: Dict[str, Any] = json.loads(f.read())


class Cell:
    """A cell is a location in the game which contains many things, a cell
    should cover a wide area such as a forest or village but villages and
    forests which cover multiple cells should be captured in the description."""
    _x: int
    _z: int
    _biome: str
    _characters: List['Character']

    def __init__(self, x: int, z: int):
        self._x = x
        self._z = z
        self._characters = []
        self.load()

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

    def get_icon(self):
        if self._biome == 'forest':
            return '\x1b[32m♣\uFE0E\x1b[0m'
        elif self._biome == 'mountain':
            return '\x1b[90m^\x1b[0m'
        elif self._biome == 'plains':
            return '\x1b[32m"\x1b[0m'
        return '\x1b[34m~\x1b[0m'

    def get_scavenge_item(self) -> Optional[Tuple[str, Dict[str, str]]]:
        scavenge_list = self._get_scavenge_list()
        if scavenge_list is None:
            return None
        item = random.choice(scavenge_list)
        return (item[0], item[1])

    def _get_scavenge_list(self) -> Optional[List[Any]]:
        """Generates the list of items that can be scavenged."""
        if self._biome not in BIOME_DATA:
            return None
        return BIOME_DATA[self._biome]['scavenge']

    @property
    def can_scavenge(self) -> bool:
        return self._get_scavenge_list is not None
