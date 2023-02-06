import inspect
import re
import itertools
from typing import Callable, TypeVar
from .adventure import Adventure

class InvalidCommandArgument(Exception):
  pass

TYPE_RE = r'typing\.Union\[(.*), NoneType\]|<class \'(.*)\'>'
DOC_RE = r'\:(.*?)\:(.*?)(\n|$)'

def requires_state(msg: str):
  def _requires_state(f):
    async def _inner(*args, **kwargs):
      return await f(*args, **kwargs)
    _inner.__wraps__ = f
    _inner.__requires_state__ = msg
    return _inner
  return _requires_state

T = TypeVar('T', bound='CommandHandlerBase')
class CommandHandlerBase:
  _adventure: Adventure
  
  def __init__(self, adventure: Adventure):
    self._adventure = adventure

  async def handle_input(self: T, input: str):
    if not input:
      return
    cmd = input.split(' ')
    commands_alias_list = list(itertools.chain([(k[8:], [doc[1].strip() for doc in re.findall(DOC_RE, getattr(v, '__wraps__', v).__doc__) if doc[0] == 'command_alias']) for k, v in self.__class__.__dict__.items() if k.startswith('command_') and getattr(v, '__wraps__', v).__doc__]))
    alias_map = {}
    for command_name, aliases in commands_alias_list:
      for alias in aliases:
        alias_map[alias] = command_name
    if cmd[0] in alias_map:
      cmd[0] = alias_map[cmd[0]]
    try:
      func = getattr(self, f'command_{cmd[0]}')
      if getattr(func, '__requires_state__', None) not in [self._adventure._state, None]:
        raise AttributeError('invalid state')
      inspect_func = getattr(func, '__wraps__', func)
      func_args = list(inspect.signature(inspect_func).parameters.values())
      if str(func_args[0].annotation) == '~T':
        func_args = func_args[1:]
      required_args_len = len([arg for arg in func_args if arg.default is inspect._empty])
      if len(cmd[1:]) < required_args_len:
        raise InvalidCommandArgument('Invalid argument length')
      args = {}
      for arg, arg_def in zip(cmd[1:], func_args):
        type_found = re.search(TYPE_RE, str(arg_def.annotation)).group(1) or re.search(TYPE_RE, str(arg_def.annotation)).group(2)
        args[arg_def.name] = __builtins__[type_found](arg)
      await func(**args)
    except InvalidCommandArgument as e:
      await self.send_message(str(e))
    except AttributeError as e:
      await self.send_message('That isn\'t a command I recognise.\n')

  def _format_help(self: T, fn: Callable):
    fn = getattr(fn, '__wraps__', fn)
    desc = 'This command has no description.'
    if fn.__doc__:
      desc_arr = [x[1] for x in re.findall(DOC_RE, fn.__doc__) if x[0] == 'command_description']
      if desc_arr:
        desc = desc_arr[0].strip()
    params = ' '.join([f'<{param.name}>' if param.default == inspect._empty else f'[{param.name}]' for param in list(inspect.signature(fn).parameters.values())[1:]])
    return f'{fn.__name__[8:]} {params} - {desc}'

  async def send_message(self: T, message: str, *args, **kwargs):
    return await self._adventure.send_message(message, *args, **kwargs)
  