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
    async def set(self, setting: str, value: str):
        """Sets a setting for the game.

        :command_summary: Sets a setting for the game.
        :command_category: System Commands
        :command_param_type setting: setting
        :command_param_type value: setting_value
        """
        pass

    @autocomplete('page')
    def autocomplete_page(self, input: List[str]):
        return []

    @autocomplete('command')
    def autocomplete_command(self, handler: CommandHandler, input: List[str]):
        """Autocomplete command functions"""
        return [c["func"].__name__ for c in handler.get_command_list()]
    
    @autocomplete('setting')
    def autocomplete_setting(self, input: List[str]):
        return ['input']
    
    @autocomplete('setting_value')
    def autocomplete_value(self, input: List[str]):
        print(input)
        if input[-2] == 'input':
            return ['sentence', 'command']
        return []
