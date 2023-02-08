import inspect
import re
import itertools
from ..game import Character
from typing import Callable, Dict, Tuple, TypeVar, List


class InvalidCommandArgument(Exception):
    pass


TYPE_RE = r'typing\.Union\[(.*), NoneType\]|typing\.(List\[.*\])|<class \'(.*)\'>'
DOC_RE = r'\:(.*?)\:(.*?)(\n|$)'


def requires_state(*args):
    def _requires_state(f):
        async def _inner(*args, **kwargs):
            return await f(*args, **kwargs)
        _inner.__wraps__ = f
        _inner.__requires_state__ = args
        _inner.__doc__ = f.__doc__
        _inner.__name__ = f.__name__
        return _inner
    return _requires_state


T = TypeVar('T', bound='CommandHandlerBase')


class CommandHandlerBase:
    """The CommandHandlerBase handles the underlying function of a command
    handler. It takes the methods from a child class and converts them into
    commands."""
    _character: Character

    def __init__(self, character: Character):
        """Constructs a CommandHandlerBase for a given character.

        :param character: The character this with handle."""
        self._character = character

    async def handle_input(self: T, cmd: List[str]):
        """Takes the input from the player and converts it to the appropriate
        function.

        :param cmd: The command from the player, already separated."""
        if not cmd[0]:
            return
        if cmd[0].startswith('\\'):
            fn = self.__class__.__dict__.get('command_say', None)
            if fn:
                await fn(self, [' '.join(cmd)[1:]])
            return
        commands_alias_list = list(
            itertools.chain(
                [(k[8:],
                  [doc[1].strip()
                   for doc in re.findall(
                       DOC_RE, getattr(v, '__wraps__', v).__doc__)
                   if doc[0] == 'command_alias']) for k,
                 v in self.__class__.__dict__.items()
                 if k.startswith('command_') and
                 getattr(v, '__wraps__', v).__doc__]))
        alias_map = {}
        for command_name, aliases in commands_alias_list:
            for alias in aliases:
                alias_map[alias] = command_name
        if cmd[0] in alias_map:
            cmd[0] = alias_map[cmd[0]]
        try:
            func = getattr(self, f'command_{cmd[0]}')
            if self._character._state not in getattr(
                    func, '__requires_state__', ['intro', 'adventure']):
                raise AttributeError('invalid state')
            inspect_func = getattr(func, '__wraps__', func)
            func_args = list(inspect.signature(
                inspect_func).parameters.values())
            if len(func_args) > 0 and str(func_args[0].annotation) == '~T':
                func_args = func_args[1:]
            required_args_len = len(
                [arg for arg in func_args if arg.default is inspect._empty])
            if len(cmd[1:]) < required_args_len:
                raise InvalidCommandArgument('Invalid argument length')
            args = {}
            for arg, arg_def in zip(cmd[1:], func_args):
                type_found = re.search(
                    TYPE_RE, str(arg_def.annotation)).group(1) or re.search(
                    TYPE_RE, str(arg_def.annotation)).group(2) or re.search(
                    TYPE_RE, str(arg_def.annotation)).group(3)
                if type_found == 'List[str]':
                    args[arg_def.name] = [' '.join(cmd[1:])]
                else:
                    args[arg_def.name] = __builtins__[type_found](arg)
            await func(**args)
        except InvalidCommandArgument as e:
            await self.send_message('game', str(e))
        except AttributeError as e:
            await self.send_message('game', 'You can\'t use that command here.\n')

    def _get_doc_data(self: T, fn: Callable) -> Tuple[str, Dict[str, str]]:
        doc = fn.__doc__
        if not doc:
            return ('No description available.', dict())
        if ':' in doc:
            desc, params = doc.split(':', 1)
            matches = re.findall(DOC_RE, ':' + params)
            desc = '\n'.join([line.strip() for line in desc.split('\n')])

            return (desc.strip(), {x[0].strip(): x[1].strip() for x in matches})
        else:
            doc = '\n'.join([line.strip() for line in doc.split('\n')])
            return (doc.strip(), {})

    def _format_help(self: T, fn: Callable):
        fn = getattr(fn, '__wraps__', fn)
        desc = 'This command has no description.'
        if fn.__doc__:
            desc_arr = [
                x[1] for x in re.findall(
                    DOC_RE,
                    fn.__doc__) if x[0] == 'command_summary']
            if desc_arr:
                desc = desc_arr[0].strip()
        params = ' '.join(
            [f'<{param.name}>'
             if param.default == inspect._empty else f'[{param.name}]'
             for param in list(inspect.signature(fn).parameters.values())
             [1:]])
        return (f'{fn.__name__[8:]} {params}', desc)

    def _get_command_list(self: T, dewrap: bool = False) -> List[Callable]:
        c_list = [
            v for k, v in self.__class__.__dict__.items()
            if k.startswith('command_') and self._character._state in getattr(
                v, '__requires_state__', ['intro', 'adventure'])]
        if dewrap:
            c_list = [getattr(v, '__wraps__', v) for v in c_list]
        return c_list

    def _get_func_param_types_list(self, command: List[str], chain: List[str]):
        return []

    async def handle_autocomplete_request(self: T, command_input: List[str]):
        if not command_input[0]:
            await self.send_message('autocomplete', '')
            return
        command_raw = [(x, x.__name__[8:],)
                       for x in self._get_command_list(dewrap=True)
                       if x.__name__[8:].startswith(command_input[0])]
        if not command_raw:
            await self.send_message('autocomplete', '')
            return
        command = command_raw[0]
        if command and len(command_input) == 1:
            await self.send_message('autocomplete', command[1] + ' ')
            return
        if command[1] != command_input[0]:
            await self.send_message('autocomplete', '')
            return
        docs = self._get_doc_data(command[0])
        types = [
            docs[1].get(f'command_param {x}', None)
            for x in list(inspect.signature(command[0]).parameters)[1:]]
        if len(types) < len(
                command_input) - 1 or not types[len(command_input) - 2]:
            await self.send_message('autocomplete', '')
            return
        prefix = ' '.join(command_input[:-1])
        suffix_list = self._get_func_param_types_list(
            command_input, types[: len(command_input) - 1])
        if not suffix_list:
            await self.send_message('autocomplete', '')
            return
        ordinal = suffix_list.index(
            command_input[-1]) if command_input[-1] in suffix_list else -2
        hidden = True
        if ordinal == len(suffix_list) - 1:
            ordinal = -1
        if ordinal == -2:
            suffix_list = [x for x in suffix_list
                           if x.startswith(command_input[-1])]
            if not suffix_list:
                await self.send_message('autocomplete', '')
                return
            hidden = False
        await self.send_message('autocomplete' if not hidden else 'autocomplete:hidden', prefix + ' ' + suffix_list[ordinal + 1])

    async def send_message(self: T, type: str, message: str, *args, **kwargs):
        return await self._character.send_message(type, message, *args, **kwargs)
