from typing import List, Optional, TypeVar

from .adventure import Adventure, CHARACTERISTIC_LIST, CHARACTERISTIC_TO_PY, TYPES_LIST
from .command_base import CommandHandlerBase, requires_state

T = TypeVar('T', bound='CommandHandler')
class CommandHandler(CommandHandlerBase):
  
  def __init__(self, adventure: Adventure):
    super().__init__(adventure)
  
  async def command_help(self: T, command: Optional[str]=None):
    """

    :command_alias: h
    :command_description: Provides help and guidance on all commands or a certain command in particular.
    :param command: test
    """
    if command is None:
      commands: List[str] = [self._format_help(v) for k, v in self.__class__.__dict__.items() if k.startswith('command_') and getattr(v, '__requires_state__', None) in [self._adventure._state, None]]
      await self.send_message('Here is a list of available commands:\n\n{}\n', '\n'.join(commands))
      return
    await self.send_message('hi\n')
  
  @requires_state('start')
  async def command_set(self: T, characteristic: str, type: str):
    """
    :command_description: Lists a group of objects.
    """
    if characteristic not in CHARACTERISTIC_LIST:
      await self.send_message('That\'s not a characteristic I can change.\n')
      return
    if type not in TYPES_LIST[characteristic]:
      await self.send_message('You cannot set {characteristic} to type.\n', characteristic)
      return
    setattr(self._adventure._character, CHARACTERISTIC_TO_PY[characteristic], type)
    self._adventure.save()
    await self.send_message('{}\n', self._adventure._character.describe_self())

  
  @requires_state('start')
  async def command_list(self: T, obj: str):
    """
    :command_description: Lists a group of objects.
    """
    if obj == 'characteristics':
      await self.send_message('Here is a list of characteristics for your character:\n\n{}\n', '\n'.join(CHARACTERISTIC_LIST))
      return
    elif obj in TYPES_LIST:
      await self.send_message('Here is a list of types for {}:\n\n{}\n', obj, '\n'.join(TYPES_LIST[obj]))
      return
    await self.send_message('That\'s not something I can list.\n')

  @requires_state('start')
  async def command_begin(self: T):
    """
    """
    self._adventure._state = 'adventure'
    self._adventure.save()
  
  @requires_state('adventure')
  async def command_survey(self: T):
    """
    
    :command_description: Surveys the immediate area, generating a map of the local cell and surrounding cells."""
    MAP = '''Local:      Global:
.........   \033[33m♣\033[0m\033[33m♣\033[0m\033[33m♣\033[0m\033[33m♣\033[0m\033[33m♣\033[0m
.........   \033[33m♣\033[0m\033[33m♣\033[0m\033[33m♣\033[0m\033[33m♣\033[0m\033[33m♣\033[0m
.........   \033[33m♣\033[0m\033[33m♣\033[0m@\033[33m♣\033[0m\033[33m♣\033[0m
..@......   ♣♣♣♣♣
.........   ♣♣♣♣♣\n'''
    await self.send_message(MAP)
