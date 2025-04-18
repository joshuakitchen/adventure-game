from collections import OrderedDict
from typing import List, Optional, TYPE_CHECKING
from .base import autocomplete, command, CommandHandler

if TYPE_CHECKING:
    from ..character import Character

CATEGORY_ORDER = [
    'Movement',
    'Interaction',
    'Combat',
    'Character',
    'Inventory',
    'System Commands',
]

def get_category_idx(category: str) -> int:
    if category not in CATEGORY_ORDER:
        return len(CATEGORY_ORDER)
    return CATEGORY_ORDER.index(category)

def flatten(xss):
    return [x for xs in xss for x in xs]

class BasicCommands:

    @command
    async def help(self, handler: CommandHandler, character: 'Character', page: Optional[str] = None):
        """Help if no commands are present will list all functions available to
        the user, otherwise it will give a detailed description of the function
        or page specified.

        :command_summary: Lists the functions or brings up help for a specific page.
        :command_category: System Commands
        :command_param_type page: page,command
        """
        if page:
            cmd = handler.get_command(page)
            if cmd:
                await character.send_message('game', '{}', cmd['desc'])
            else:
                await character.send_message('game', 'Command not found.\n')
            return
        cmd_list = sorted(handler.get_command_list(), key=lambda c: (get_category_idx(c.get('category', 'Misc')), c['func'].__name__))
        categories = OrderedDict()
        for c in cmd_list:
            category = c.get('category', 'Misc')
            if category not in categories:
                categories[category] = []
            categories[category].append([f'@lbl@{c["func"].__name__}@res@ {" ".join(c["doc_param"])}', c['summary']])
        max_len = max([len(cmd[0]) for c in categories.values() for cmd in c])
        for c in flatten(categories.values()):
            c[0] = c[0].ljust(max_len, ' ')
        
        command_str = ''

        for category, cmds in categories.items():
            command_str += f'=== {category} ===\n'
            for cmd in cmds:
                command_str += f'{cmd[0]} - {cmd[1]}\n'
            command_str += '\n'
        await character.send_message('game', '{}\n', command_str)

    @command
    async def clear(self):
        """Clears the terminal, this command is client side so it will continue
        to work even if the server is down.

        :command_summary: Clears the terminal.
        :command_category: System Commands"""
        pass

    @command
    async def set(self, c: 'Character', setting: str, value: str):
        """Sets a setting for the game which can either be client or server
        side.

        The following settings are available:
        - input - Sets the input type for the game, can be either sentence or command.
        - scroll - Whether to scroll smoothly or instantly, can be either smooth or instant.
        - map_on_survey - Whether to show the map on the survey screen, can be either true or false.

        :command_summary: Sets a setting for the game.
        :command_category: System Commands
        :command_param_type setting: setting
        :command_param_type value: setting_value
        """
        if setting == 'input':
            await c.set_setting('input', value)
            if value == 'sentence':
                await c.send_message('game', 'You are now in sentence input mode, you should now type in sentences to interact with the game.')
            elif value == 'command':
                await c.send_message('game', 'You are now in command input mode, you should now type in commands to interact with the game.')
            else:
                await c.send_message('game', 'Invalid setting.')
        elif setting == 'scroll':
            await c.set_setting('scroll', value)
            await c.send_message('game', 'Now scrolling using {}.', value)
        elif setting == 'map_on_survey':
            if value == 'true':
                await c.set_setting('map_on_survey', True)
                await c.send_message('game', 'Map will now be shown on the survey screen.')
            elif value == 'false':
                await c.set_setting('map_on_survey', False)
                await c.send_message('game', 'Map will not be shown on the survey screen.')
        else:
            await c.send_message('game', 'Setting not found.')

    @autocomplete('page')
    def autocomplete_page(self, input: List[str]):
        return []

    @autocomplete('command')
    def autocomplete_command(self, handler: CommandHandler, input: List[str]):
        """Autocomplete command functions"""
        return [c["func"].__name__ for c in handler.get_command_list()]
    
    @autocomplete('setting')
    def autocomplete_setting(self, input: List[str]):
        return ['input', 'scroll', 'map_on_survey']
    
    @autocomplete('setting_value')
    def autocomplete_value(self, input: List[str]):
        if input[-2] == 'input':
            return ['sentence', 'command']
        elif input[-2] == 'scroll':
            return ['smooth', 'instant']
        elif input[-2] == 'map_on_survey':
            return ['true', 'false']
        return []
