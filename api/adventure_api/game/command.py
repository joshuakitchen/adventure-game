from typing import List, Optional, TypeVar

from .world import World
from ..util.command_base import CommandHandlerBase, requires_state

T = TypeVar('T', bound='CommandHandler')


class CommandHandler(CommandHandlerBase):
    """The CommandHandler class holds all the commands in the game"""

    async def command_help(self: T, message: Optional[str] = None):
        """Either sends a list of all commands to the player or if a page is
        present, sends a detailed description of page or command that is
        documented."""
        commands = [self._format_help(x) for x in self._get_command_list()]
        await self.send_message('game', 'Here is a list of commands you can use in the current context:\n{}\n\n', '\n'.join(commands))

    @requires_state('intro')
    async def command_begin(self: T, name: List[str]):
        """Starts the game and sets your character name."""
        actual_name = ' '.join(name)
        if len(actual_name) > 20:
            await self.send_message('game', 'Your name must be below 20 characters.')
            return
        self._character._name = ' '.join(name)
        self._character._state = 'adventure'
        self._character.save_character()

    @requires_state('adventure')
    async def command_say(self: T, message: List[str]):
        """Sends a message to every player on the game.

        :command_summary: Chat to other people"""
        await World.send_to_all('chat', '\x1b[92m{}\x1b[0m: {}\n', self._character._name, ' '.join(message))

    async def command_clear(self: T):
        """Clears the terminal

        :command_summary: Clears the terminal"""
        pass  # Placeholder for the client only clear command
