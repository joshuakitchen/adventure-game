import json
import random
from fastapi import WebSocket
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from .colors import replace_colors
from .world import World
from .item import Item
from ..config import get_conn

if TYPE_CHECKING:
    from .cell import Cell

TITLE = ''' _  _            _     _ _   _
| \\| |_  _ _ __ (_)_ _(_) |_| |_
| .` | || | '  \\| | '_| |  _| ' \\
|_|\\_|\\_, |_|_|_|_|_| |_|\\__|_||_|
      |__/'''

INTRODUCTION_TEXT = '''{}

Welcome to the world of Nymirith.

Type "begin" followed by your character name to start.
\n\n'''


SCAVENGE_TIMER = 3
SCAVENGE_CHANCE = 0.6


class Character:
    """The Character class handles the data for a single character within the
    game, this represents a person connected through a WebSocket."""
    _id: str
    _ws: WebSocket
    _state: str
    _name: Optional[str]
    _x: int
    _z: int
    _cell: Optional['Cell']
    _inventory: List[Tuple[str, Dict[str, str]]]
    _action: Optional[str]
    _action_timer: int

    def __init__(self, id: str, ws: WebSocket):
        """Constructs the Character

        :param id: The user id.
        :param ws: The websocket the user is connected with."""
        self._id = id
        self._ws = ws
        self._state = 'intro'
        self._name = None
        self._x = 0
        self._z = 0
        self._action = None
        self._action_timer = 0
        self._inventory = [('stick', dict(material='oak'))]
        self.load_character()

    async def handle_login(self):
        """Handles the character entering the world, this will take place just
        after the WebSocket connection and should provide either an introduction
        for new players, or an update for old players."""
        if self._state == 'intro':
            await self.send_message('game', INTRODUCTION_TEXT, TITLE, 'test')
        else:
            await self.send_message('game', '{}\n\nWelcome back, @lgr@{}@res@.\n\n', TITLE, self._name)
            self._cell = World.load_cell(self._x, self._z, self)

    async def handle_logout(self):
        """Handles the user leaving the websocket."""
        if self._state == 'intro':
            return
        World.unload_cell(self._x, self._z, self)

    async def tick(self):
        """Handles the game tick, the tick is every 600ms and is used so that
        actions which are repeating can be done until the player is done."""
        if self._action_timer > 0:
            self._action_timer = self._action_timer - 1
            return
        if self._cell is None:
            return
        if self._action == 'scavenge':
            if random.random() > SCAVENGE_CHANCE:
                item = self._cell.get_scavenge_item()
                if item:
                    self._inventory.append(item)
                    await self.send_message('game', 'You find a @yel@{}@res@\n', Item.get_display_name(item))
            self._action_timer = SCAVENGE_TIMER

    async def set_action(self, action: Optional[str]):
        """Sets the players current action, if the action is currently set then
        stops the previous action. If the action is None then the action is
        stopped completely.

        :param action: The action"""
        if self._action == action:
            if action is None:
                await self.send_message('game', 'You\'re already not doing anything.\n')
                return
            await self.send_message('game', 'You are already doing that.\n')
            return
        if not self._cell:
            return
        if self._action == 'scavenge':
            if not self._cell.can_scavenge:
                await self.send_message('game', 'You can\'t find anything of use here.')
                self.action = None
                return
            await self.send_message('game', 'You stop scavenging.\n')
        if action == 'scavenge':
            await self.send_message('game', 'You begin scavenging for whatever you can find.\n')
            self._action_timer = SCAVENGE_TIMER
        self._action = action

    async def send_message(self, type: str, message: str, *args, **kwargs):
        """Sends a message to the Characters connected WebSocket.

        :param type: The type of request to send (game,chat,stats,error).
        :param message: The message to send.
        :param *args: Formats the message with the given arguments.
        :param **kwargs: Formats the message with the given kwargs."""
        message = replace_colors(message.format(*args, **kwargs))
        await self._ws.send_json(dict(type=type, data=message))

    def to_json(self) -> str:
        """Converts the character to JSON for saving."""
        return json.dumps(
            dict(
                state=self._state, name=self._name, x=self._x,
                z=self._z))

    def from_json(self, raw_data: str):
        """Converts the character back from JSON for loading.

        :param data: The data as a string."""
        data: Dict[str, Any] = json.loads(raw_data)
        self._state = data.get('state', 'intro')
        self._name = data.get('name', None)
        self._x = data.get('x', 0)
        self._z = data.get('z', 0)

    def load_character(self):
        """Loads the character using the current database driver."""
        driver, conn = get_conn()
        if driver == 'sqlite':
            pass  # TODO: implement the sqlite driver
        elif driver == 'postgres':
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT state FROM users WHERE id = %s', [self._id])
                data = cur.fetchone()
            if data and data[0]:
                self.from_json(data[0])

    def save_character(self):
        """Saves the character using the current database driver."""
        driver, conn = get_conn()
        if driver == 'sqlite':
            pass  # TODO: implement the sqlite driver
        elif driver == 'postgres':
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE users SET state = %s WHERE id = %s', [
                        self.to_json(), self._id])
                conn.commit()

    @property
    def inventory(self):
        return [Item.get_item_properties(item) for item in self._inventory]
