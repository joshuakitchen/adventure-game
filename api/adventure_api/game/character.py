import json
import random
from fastapi import WebSocket
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from .commands import BasicCommands, ChatCommands, CombatCommands, CommandHandler, IntroCommands, ItemCommands, WorldCommands
from .colors import replace_colors
from .world import World
from .item import Item
from config import get_conn
from util import generate_id

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
    _instance_id: str
    _ws: WebSocket
    _state: str
    _name: Optional[str]
    _x: int
    _z: int
    _cell: Optional['Cell']
    _inventory: List[Tuple[str, Dict[str, str]]]
    _action: Optional[str]
    _action_timer: int
    _attributes: Dict[str, Tuple[int, int]]
    _skills: Dict[str, Tuple[int, int]]
    _command_handler: CommandHandler
    _target: Optional[str]

    def __init__(self, id: str, ws: WebSocket):
        """Constructs the Character

        :param id: The user id.
        :param ws: The websocket the user is connected with."""
        self._id = id
        self._instance_id = generate_id(0)
        self._ws = ws
        self._state = 'intro'
        self._name = None
        self._x = 0
        self._z = 0
        self._action = None
        self._action_timer = 0
        self._inventory = []
        self._cell = None
        self._hp = 10
        self._attributes = dict(
            constitution=(10, 1),
            strength=(1, 1),
            magic=(1, 1),
            dexterity=(1, 1)
        )
        self._command_handler = CommandHandler(self)
        self._command_handler.add_command_handler(BasicCommands())
        self.load_character()
        self.set_state(self._state)

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
                if self.add_item(*item):
                    await self.send_message('game', 'You find a @yel@{}@res@\n', Item.get_display_name(item))
                else:
                    await self.send_message('game', 'Unable to add item, your inventory is full.\n')
                    self._action = None
            self._action_timer = SCAVENGE_TIMER
        elif self._action == 'attack':
            target = self.target
            if target is None:
                self._target = None
                return
            hit = max(1, self.max_hit)
            target.damage(self._instance_id, 1)
            await self.send_message('game', 'You hit the @red@{}@res@ for @red@{}@res@ damage, it looks {}\n', target.name, hit, target.damage_state)
            if target.is_dead:
                await self.send_message('game', 'You kill the @red@{}@res@\n', target.name)
                self._target = None
                self._action = None
            self._action_timer = 3

    async def damage(self, enemy_id: str, damage: int):
        if not self._cell:
            return
        e = self._cell.get(enemy_id)
        if not e:
            return
        self._hp = max(0, self._hp - damage)
        await self.send_message('game', 'You take @red@{}@res@ damage from @red@{}@res@, you\'re now on {}/{} hp.\n', damage, e.name, self._hp, self._attributes['constitution'][0])

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
        if self._action == 'attack':
            await self.send_message('game', 'You stop attacking the @red@{}@res@.\n', self.target.name)
            self._target = None
        if action == 'scavenge':
            await self.send_message('game', 'You begin scavenging for whatever you can find.\n')
            self._action_timer = SCAVENGE_TIMER
        elif action == 'attack':
            await self.send_message('game', 'You begin attacking the @red@{}@res@\n', self.target.name)
        self._action = action

    async def send_message(self, type: str, message: str, *args, **kwargs):
        """Sends a message to the Characters connected WebSocket.

        :param type: The type of request to send (game,chat,stats,error).
        :param message: The message to send.
        :param *args: Formats the message with the given arguments.
        :param **kwargs: Formats the message with the given kwargs."""
        message = replace_colors(message.format(*args, **kwargs))
        await self._ws.send_json(dict(type=type, data=message))

    def set_state(self, state: str):
        """Sets the state of this character.

        :param state: The state to set the character in."""
        if self._state == 'intro':
            self._command_handler.remove_command_handler(IntroCommands)
        elif self._state == 'adventure':
            self._command_handler.remove_command_handler(WorldCommands)
            self._command_handler.remove_command_handler(ChatCommands)
            self._command_handler.remove_command_handler(CombatCommands)
            self._command_handler.remove_command_handler(ItemCommands)
        self._state = state
        if self._state == 'adventure':
            self._command_handler.add_command_handler(WorldCommands())
            self._command_handler.add_command_handler(ChatCommands())
            self._command_handler.add_command_handler(CombatCommands())
            self._command_handler.add_command_handler(ItemCommands())
        elif self._state == 'intro':
            self._command_handler.add_command_handler(IntroCommands())

    async def start_attacking(self, target_id: str):
        """Begins attacking the target with the given target id."""
        if self._cell is None:
            return
        if not self._cell.get(target_id):
            return
        self._target = target_id
        await self.set_action('attack')

    def add_item(self, item_id: str, qualifiers: Dict[str, Any]) -> bool:
        """"""
        item = Item.get_item_properties((item_id, qualifiers,))
        if self.free_slots - item['slots_taken'] < 0:
            return False
        self._inventory.append((item_id, qualifiers))
        return True

    def remove_item_at(self, slot: int):
        if slot >= len(self._inventory):
            return
        del self._inventory[slot]

    def to_json(self) -> str:
        """Converts the character to JSON for saving."""
        return json.dumps(dict(inventory=self._inventory))

    def from_json(self, raw_data: Tuple[str, int, int, str, str]):
        """Converts the character back from JSON for loading.

        :param data: The data as a string."""
        self._name = raw_data[0]
        self._x = raw_data[1]
        self._z = raw_data[2]
        self._state = raw_data[3]
        data: Dict[str, Any] = json.loads(raw_data[4])
        self._inventory = data.get('inventory', [])

    def load_character(self):
        """Loads the character using the current database driver."""
        driver, conn = get_conn()
        if driver == 'sqlite':
            pass  # TODO: implement the sqlite driver
        elif driver == 'postgres':
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT name, x, z, state, additional_data FROM users WHERE id = %s', [
                        self._id])
                data = cur.fetchone()
            if data:
                self.from_json(data)

    def save_character(self):
        """Saves the character using the current database driver."""
        driver, conn = get_conn()
        if driver == 'sqlite':
            pass  # TODO: implement the sqlite driver
        elif driver == 'postgres':
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE users SET name = %s, x = %s, z = %s, state = %s, additional_data = %s WHERE id = %s', [
                        self._name, self._x, self._z, self._state, self.to_json(), self._id])
                conn.commit()

    @property
    def name(self):
        return self._name

    @property
    def max_hit(self):
        return 1

    @property
    def target(self):
        if not self._cell:
            return None
        if self._target is None:
            return None
        return self._cell.get(self._target)

    @property
    def inventory(self):
        return [Item.get_item_properties(item) for item in self._inventory]

    @ property
    def command_handler(self):
        return self._command_handler

    @ property
    def free_slots(self):
        return 5 - sum([i['slots_taken'] for i in self.inventory])
