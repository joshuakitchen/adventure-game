from typing import TYPE_CHECKING
from .base import command

if TYPE_CHECKING:
    from ..character import Character


class IntroCommands:

    @command
    async def begin(self, character: 'Character', *name):
        """Begins your adventure by setting your name.

        :command_summary: Begin your adventure by setting your name."""
        name_str = ' '.join(name).strip()
        if not name_str:
            await character.send_message('game', 'You must specify a name, try "begin <name>"\n')
            return
        if len(name_str) > 12:
            await character.send_message('game', 'Character name must be below 12 characters.\n')
            return
        character._name = name_str
        character.set_state('adventure')
        await character.send_message('game', 'Welcome @lgr@{}@res@!\nUse "help" to list commands to get started.\n', name_str)
