from typing import List, Optional, TypeVar

from .item import Item
from .world import World
from ..util.command_base import CommandHandlerBase, requires_state

T = TypeVar('T', bound='CommandHandler')

SURVEY_WIDTH = 14
SURVEY_HEIGHT = 7


class CommandHandler(CommandHandlerBase):
    """The CommandHandler class holds all the commands in the game"""

    async def command_help(self: T, command: Optional[str] = None):
        """Either sends a list of all commands to the player or if a page is
        present, sends a detailed description of page or command that is
        documented.

        :command_alias: h
        :command_summary: Displays help information"""
        if command is None:
            commands = [self._format_help(x) for x in self._get_command_list()]
            longest = max([len(v) for v, _ in commands])
            command_print = [
                c.ljust(
                    longest,
                    ' ') +
                ' - ' +
                d for c,
                d in commands]
            await self.send_message('game', 'Here is a list of commands you can use in the current context:\n{}\n\n', '\n'.join(command_print))
            return
        cmd = [x for x in self._get_command_list()
               if x.__name__ == f'command_{command}']
        if not cmd:
            await self.send_message('game', '@red@No such command: {}@res@\n', command)
            return
        desc, params = self._get_doc_data(cmd[0])
        aliases = params.get('command_alias', None)
        await self.send_message('game', '{}\n\n', desc)
        if aliases:
            await self.send_message('game', 'Aliases: {}\n\n', aliases)

    @requires_state('intro')
    async def command_begin(self: T, name: List[str]):
        """Starts the game and sets your character name."""
        actual_name = ' '.join(name)
        if len(actual_name) > 20:
            await self.send_message('game', 'Your name must be below 20 characters.')
            return
        self._character._name = ' '.join(name)
        self._character._state = 'adventure'
        self._character._cell = World.load_cell(
            self._character._x, self._character._z, self._character)
        self._character.save_character()

    @requires_state('adventure')
    async def command_say(self: T, message: List[str]):
        """Sends a message to every player on the game.

        :command_summary: Chat to other people"""
        await World.send_to_all('chat', '\x1b[92m{}\x1b[0m: {}\n', self._character._name, ' '.join(message))

    @requires_state('adventure')
    async def command_survey(self: T):
        """Surveys the surrounding area, generates a minimap of the visible area
        and also lists entities and resources nearby.

        :command_alias: sv
        :command_summary: Surveys the surrounding area"""
        m = ''

        for z in range(SURVEY_HEIGHT):
            for x in range(SURVEY_WIDTH):
                cx = self._character._x + x - int(SURVEY_WIDTH / 2)
                cz = self._character._z + z - int(SURVEY_HEIGHT / 2)
                cell = World.get_cell(cx, cz)
                if self._character._x == cx and self._character._z == cz:
                    m = m + '\x1b[91m@\x1b[0m'
                else:
                    m = m + cell.get_icon()
            m = m + '\n'
        await self.send_message('game', '{}\n\nYou can see:\n@lgr@{}@res@\n', m, '\n'.join([c._name for c in self._character._cell._characters]))

    @requires_state('adventure')
    async def command_scavenge(self: T):
        """Begin scavenging the area for resources, the resources found will
        depend on the type of are you're in.

        :command_alias: sc
        :command_summary: Begin scavenging action."""
        await self._character.set_action('scavenge')

    @requires_state('adventure')
    async def command_stop(self: T):
        """If the player is doing an action, stops the action as soon as
        it\'s possible.

        :command_alias: st
        :command_summary: Stops the current action."""
        await self._character.set_action(None)

    @requires_state('adventure')
    async def command_inventory(self: T):
        """Lists the players current inventory items and the space available,
        each item takes up a certain amount of slots and if the player does not
        have capacity to hold an item, the item will be dropped on the floor for
        a certain amount of time.

        Wearing a container like a backpack can help increase the amount of
        slots you have available.

        :command_alias: ci
        :command_summary: Lists the players current inventory and space."""
        await self.send_message('game', 'You are currently carrying:\n{}\n', '\n'.join([f"@yel@{item['name']}@res@" for item in self._character.inventory]))

    async def command_clear(self: T):
        """Clears the terminal

        :command_alias: cls
        :command_summary: Clears the terminal"""
        pass  # Placeholder for the client only clear command
