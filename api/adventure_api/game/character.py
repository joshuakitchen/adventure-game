import json
import random
import logging
from fastapi import WebSocket
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from .commands import BasicCommands, CharacterCommands, ChatCommands, CombatCommands, CommandHandler, IntroCommands, ItemCommands, WorldCommands
from .colors import replace_colors
from .world import World
from .item import Item
from config import get_conn
from util import generate_id, EXP_TABLE

if TYPE_CHECKING:
    from .cell import Cell
    from .enemy import Enemy

logger = logging.getLogger(__name__)

TITLE = ''' _  _            _     _ _   _
| \\| |_  _ _ __ (_)_ _(_) |_| |_
| .` | || | '  \\| | '_| |  _| ' \\
|_|\\_|\\_, |_|_|_|_|_| |_|\\__|_||_|
      |__/'''

INTRODUCTION_TEXT = '''{}

Welcome to the world of Nymirith.

Your story is your own, you can choose to be a hero, a villain, or something in,
in-between. Become a legendary fighter, a king of the land, or a master
fisherman. The choice is yours.

The game has two input modes.
- Command Mode: Command mode is rigid and requires you to type commands in a
    specific format. This mode is powerful and allows discrete control over your
    character, but prevents you from using sentences. Spelling mistakes will
    be suggested but not input automatically.
- Sentence Mode: Sentence mode is more relaxed and allows you to type in full
    sentences to achieve your goal, these are converted to commands but offer
    synonyms and more natural language. Spelling mistakes will be corrected and
    input automatically with the closest match within reason, if this happens
    the corrected word will be highlighted.

The game is a set to "{}" mode, you can change this by typing
"@lbl@set@res@ input sentence" or "@lbl@mode@res@ input command".

Type "@lbl@begin@res@" followed by your character name to start.
\n\n'''


SCAVENGE_TIMER = 1
SCAVENGE_CHANCE = 0.6


class Character:
    """The Character class handles the data for a single character within the
    game, this represents a person connected through a WebSocket."""
    _id: str
    _instance_id: str
    _ws: WebSocket
    _session_id: str
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
    _disconnected: bool

    def __init__(self, id: str, ws: WebSocket, session_id: str):
        """Constructs the Character

        :param id: The user id.
        :param ws: The websocket the user is connected with."""
        self._id = id
        self._instance_id = generate_id(0)
        self._ws = ws
        self._session_id = session_id
        self._disconnected = False
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
            constitution=[10, 1],
            strength=[1, 1],
            magic=[1, 1],
            dexterity=[1, 1]
        )
        self._skills = dict()
        self._command_handler = CommandHandler(self)
        self._command_handler.add_command_handler(BasicCommands())
        self.load_character()
        self.set_state(self._state)

    async def handle_login(self, send_motd: bool = True):
        """Handles the character entering the world, this will take place just
        after the WebSocket connection and should provide either an introduction
        for new players, or an update for old players."""
        if self._state == 'intro':
            if send_motd:
                await self.send_message('game', INTRODUCTION_TEXT, TITLE, 'test')
                await self.send_message('chat', '@lgr@You are connected to the global chat channel.@res@\n')
        else:
            if send_motd:
                await self.send_message('game', '{}\n\nWelcome back, @lgr@{}@res@.\nType \"@lbl@help@res@\" to see available commands.\n\n', TITLE, self._name)
                await self.send_message('chat', '@lgr@You are connected to the global chat channel.@res@\n')
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
                
                for k, v in item[1].items():
                    if v.startswith('script:'):
                        fn = getattr(Item, v[7:])
                        item[1][k] = fn(character=self)

                if self.add_item(*item):
                    aan = 'an' if Item.get_display_name(item).lower()[0] in 'aeiou' else 'a'

                    await self.send_message('game', 'You find {} @yel@{}@res@', aan, Item.get_display_name(item))
                    
                    await Item.handle_script(item, 'on_scavenge', character=self)
                else:
                    await self.send_message('game', 'Unable to add item, your inventory is full.')
                    self._action = None
            # else:
            #     await self.send_message('game', 'You find nothing of use.')
            self._action_timer = SCAVENGE_TIMER
        elif self._action == 'attack':
            target = self.target
            if target is None:
                self._target = None
                return
            hit = random.randint(1, self.max_hit)
            target.damage(self._instance_id, hit)

            xp_gain = 2 * hit

            if not 'barehanded' in self._skills:
                level = 0
                while xp_gain >= EXP_TABLE[level]:
                    xp_gain -= EXP_TABLE[level]
                    level += 1
                self._skills['barehanded'] = [level + 1, xp_gain]
                await self.send_message('game', 'You begin to learn the art of barehanded combat.')
            else:
                level, xp = self._skills['barehanded']
                if level < 100:
                    xp += xp_gain
                    level_gained = False
                    while xp >= EXP_TABLE[level - 1]:
                        level += 1
                        level_gained = True
                    if level_gained:
                        await self.send_message('game', 'You have gained a level in barehanded combat.\n')
                    self._skills['barehanded'] = (level, xp)

            await self.send_message('game', 'You hit the @red@{}@res@ for @red@{}@res@ damage, it looks {}', target.name, hit, target.damage_state)
            if target.is_dead:
                await self.send_message('game', 'You kill the @red@{}@res@', target.name)
                if 'on_defeat' in target.data:
                    print(target.data['on_defeat'], target, self, self._cell)
                    await target.data['on_defeat'](target, self, self._cell)
                self._target = None
                self._action = None
            self._action_timer = 3

    async def process_script(self, script: List[Any], *args, **kwargs):
        """Processes a script for the character.

        :param script: The script to process."""
        for action in script:
            if action[0] == 'message':
                await self.send_message('game', action[1])
            elif action[0] == 'add_exp':
                skill = action[1]
                xp = action[2]
                if not skill in self._skills:
                    self._skills[skill] = [1, 0]
                level, current_xp = self._skills[skill]
                current_xp += xp
                while current_xp >= EXP_TABLE[level - 1]:
                    current_xp -= EXP_TABLE[level - 1]
                    level += 1
                self._skills[skill] = (level, current_xp)

    async def damage(self, enemy_id: str, damage: int) -> bool:
        if not self._cell:
            return False
        e = self._cell.get(enemy_id)
        if not e:
            return False
        self._hp = max(0, self._hp - damage)
        await self.send_message('game', 'You take @red@{}@res@ damage from @red@{}@res@, you\'re now on {}/{} hp.\n', damage, e.name, self._hp, self._attributes['constitution'][0])
        if self._hp <= 0:
            await self.on_dead()
            return True
        return False

    async def on_dead(self):
        await self.send_message('game', 'Oh dear, you have died!\n')
        self._inventory = []
        self._hp = self._attributes['constitution'][0]
        self._target = None
        self._action = None
        self._action_timer = 0
        self.move(0, 0)

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
        if self._ws is None or self._ws.client_state.value != 1:
            return
        message = replace_colors(message.format(*args, **kwargs))
        await self._ws.send_json(dict(type=type, data=message))

    def set_state(self, state: str):
        """Sets the state of this character.

        :param state: The state to set the character in."""
        if self._state == 'intro':
            self._command_handler.remove_command_handler(IntroCommands)
        elif self._state == 'adventure':
            self._command_handler.remove_command_handler(CharacterCommands)
            self._command_handler.remove_command_handler(WorldCommands)
            self._command_handler.remove_command_handler(ChatCommands)
            self._command_handler.remove_command_handler(CombatCommands)
            self._command_handler.remove_command_handler(ItemCommands)
        self._state = state
        if self._state == 'adventure':
            self._command_handler.add_command_handler(CharacterCommands())
            self._command_handler.add_command_handler(WorldCommands())
            self._command_handler.add_command_handler(ChatCommands())
            self._command_handler.add_command_handler(CombatCommands())
            self._command_handler.add_command_handler(ItemCommands())
        elif self._state == 'intro':
            self._command_handler.add_command_handler(IntroCommands())
        self.save_character()

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
        item = self._inventory[slot]
        del self._inventory[slot]
        return item

    def move(self, x: int, z: int):
        """Moves to the specified cell.

        :param x: The x coordinate.
        :param z: The z coordinate."""
        ox, oz = self._x, self._z
        self._x = x
        self._z = z
        World.unload_cell(ox, oz, self)
        self._cell = World.load_cell(x, z, self)

    def to_json(self) -> str:
        """Converts the character to JSON for saving."""
        return json.dumps(dict(hp=self._hp, inventory=self._inventory, attributes=self._attributes, skills=self._skills, action_timer=self._action_timer))

    def from_json(self, raw_data: Tuple[str, int, int, str, str]):
        """Converts the character back from JSON for loading.

        :param data: The data as a string."""
        self._name = raw_data[0]
        self._x = raw_data[1]
        self._z = raw_data[2]
        self._state = raw_data[3]
        data: Dict[str, Any] = json.loads(raw_data[4])
        self._hp = data.get('hp', self._hp)
        self._inventory = data.get('inventory', [])
        self._attributes = data.get('attributes', self._attributes)
        self._skills = data.get('skills', self._skills)
        self._action_timer = data.get('action_timer', self._action_timer)

    def load_character(self):
        """Loads the character using the current database driver."""
        driver, conn = get_conn()
        if driver == 'sqlite':
            try:
                cur = conn.cursor()
                try:
                    cur.execute(
                        'SELECT name, x, z, state, additional_data FROM users WHERE id = ?', [
                            self._id])
                    data = cur.fetchone()
                    if data:
                        self.from_json(data)
                finally:
                    cur.close()
            finally:
                conn.close()
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
            try:
                conn.execute(
                    'UPDATE USERS SET name = ?, x = ?, z = ?, state = ?, additional_data = ? WHERE id = ?', [
                        self._name, self._x, self._z, self._state, self.to_json(), self._id])
                conn.commit()
            finally:
                conn.close()
        elif driver == 'postgres':
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE users SET name = %s, x = %s, z = %s, state = %s, additional_data = %s WHERE id = %s', [
                        self._name, self._x, self._z, self._state, self.to_json(), self._id])
                conn.commit()
        logger.info('saved character [%s] [%s]', self._id, self._name)

    def get_skill_level(self, name: str) -> int:
        return self._skills.get(name, (1, 0))[0]

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def faction(self) -> str:
        return 'Independent'
    
    @property
    def health(self) -> int:
        return self._hp
    
    @health.setter
    def health(self, value: int):
        self._hp = max(0, min(value, self._attributes['constitution'][0]))

    @property
    def max_hit(self):
        strength_level = self._attributes['strength'][0]
        skill_level = self.get_skill_level('barehanded')

        a = (strength_level + skill_level) / 4.0
        if a < 1:
            a = 1

        return int(a)

    @property
    def target(self) -> 'Enemy':
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
    
    @property
    def coordinate(self):
        return self._x, self._z
    
    @property
    def coordinate_str(self) -> str:
        return f'{self._x},{self._z}'
