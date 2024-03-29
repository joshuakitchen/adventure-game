from typing import List, Optional, TYPE_CHECKING
from .base import autocomplete, command, CommandHandler

if TYPE_CHECKING:
    from ..character import Character


class BasicCommands:

    @command
    async def help(self, handler: CommandHandler, character: 'Character', page: Optional[str] = None):
        """Help if no commands are present will list all functions available to
        the user, otherwise it will give a detailed description of the function
        or page specified.

        :command_summary: Lists the functions or brings up help for a specific page.
        :command_param_type page: page,command
        """
        cmds = [
            (f'{c["func"].__name__} {" ".join(c["doc_param"])}', c['summary'])
            for c in handler.get_command_list()
        ]
        max_len = max([len(c[0]) for c in cmds])
        cmds = [(c[0].ljust(max_len, ' '), c[1]) for c in cmds]
        commands = [
            f'{c[0]} - {c[1]}'
            for c in cmds]
        command_str = '\n'.join(commands)
        await character.send_message('game', '{}\n', command_str)

    @command
    async def clear(self):
        """Clears the terminal.

        :command_summary: Clears the terminal."""
        pass

    @autocomplete('page')
    def autocomplete_page(self, input: List[str]):
        return []

    @autocomplete('command')
    def autocomplete_command(self, handler: CommandHandler, input: List[str]):
        """Autocomplete command functions"""
        return [c["func"].__name__ for c in handler.get_command_list()]
