from noise import snoise2
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character

HEIGHT_SCALE = 60
TREE_SCALE = 30


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
