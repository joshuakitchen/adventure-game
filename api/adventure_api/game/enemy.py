import json
from util import generate_id
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .cell import Cell
    from .character import Character

ENEMY_DATA = {}

class Enemy:
    _instance_id: str
    _internal_name: str
    _current_hp: int
    _cell: 'Cell'
    _target: Optional[str]
    _timer: int
    _collectives: Dict[str, Dict[str, Any]] = {}

    def __init__(self, cell: 'Cell', internal_name: str):
        self._cell = cell
        self._internal_name = internal_name
        self._current_hp = self.data['hp']
        self._instance_id = generate_id(1)
        self._target = None
        self._timer = 0

    async def tick(self):
        if self._timer > 0:
            self._timer = self._timer - 1
            return
        if self._target is None:
            return
        if self.target is None:
            self._target = None
            return
        is_dead = await self.target.damage(self.id, 1)
        if is_dead:
            self._target = None
        self._timer = self.data['attack_timer']

    def damage(self, enemy_id: str, damage: int):
        self._current_hp = max(0, self._current_hp - damage)
        if not self._target:
            self._target = enemy_id
        if self.is_dead:
            self._cell.remove(self)

    @property
    def id(self) -> str:
        return self._instance_id

    @property
    def unique_number(self) -> int:
        return int(self.id[:-2], 16)

    @property
    def name(self) -> str:
        return self.data['name']

    @property
    def description(self) -> str:
        return self.data['description'][self.unique_number %
                                        len(self.data['description'])]

    @ property
    def damage_state(self) -> str:
        perc = self._current_hp / self.data['hp']
        if perc == 1:
            return f'unharmed'
        elif perc >= 0.9:
            return 'practically unharmed'
        elif perc >= 0.7:
            return 'like it has some scrapes'
        elif perc >= 0.5:
            return 'like it\'s in pain'
        elif perc >= 0.25:
            return 'like it\'s in a lot of pain'
        return 'like it\'s on it\'s last legs'

    @ property
    def data(self) -> Dict[str, Any]:
        return ENEMY_DATA[self._internal_name]

    @ property
    def is_dead(self) -> bool:
        return self._current_hp == 0

    @ property
    def target(self) -> Optional['Character']:
        if not self._target:
            return None
        return self._cell.get(self._target)  # type: ignore
    
    @classmethod
    def get_collective(cls, collective_id: str) -> Optional[Dict[str, Any]]:
        return cls._collectives.get(collective_id, None)


def register_enemy(data):
    ENEMY_DATA[data['id']] = data
    Enemy._collectives[data['collective_id']] = ENEMY_DATA[data['id']]
