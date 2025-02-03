import functools
import itertools
import inspect
import re
from collections import OrderedDict
from typing import Any, Callable, Iterable, List, Type, Union, TYPE_CHECKING

from util import find_closest_match

if TYPE_CHECKING:
    from ..character import Character

DOC_STRING = r'\:\s*(.*?)\:\s*(.*?)\s*($|\n)'


def _parse_documentation(fn: Callable):
    """Parses the command documentation and returns a dictionary of values which
    contain the different parameters related to functions, this will be used for
    passing help information onto the player.

    Due to this all being in code comments it also provides input as to what the
    function should do in the game.

    :param fn: The function to parse."""
    doc = getattr(fn, '__doc__', None)
    if not doc:
        return dict(desc='', summary='This command has no summary.', params=[])
    if ':' not in doc:
        desc = '\n'.join([line.strip() for line in doc.split('\n')])
        return dict(
            desc=desc, summary='This command has no summary.', params=[])
    desc, args_string = doc.split(':', 1)
    desc = '\n'.join([line.strip() for line in desc.split('\n')]).strip()
    args = [(k.split(' '), v)
            for k, v, _ in re.findall(DOC_STRING, ':' + args_string)]
    summary = 'This command has no summary.'
    category = 'Misc'
    params = []
    for arg in args:
        arg_type = arg[0][0]
        if arg_type == 'command_summary':
            summary = arg[1]
        elif arg_type == 'command_category':
            category = arg[1]
        elif arg_type == 'command_param_type':
            params.append(arg[1].split(','))  # type: ignore
    return dict(desc=desc, summary=summary, category=category, params=params)


def _parse_command_help_params(f, doc):
    """Parses the help parameters of the currently specified function, this
    will check if the commands are marked as optional or not and mark the param
    accordingly.

    It will also use information from the documentation parser to determine what
    could be within the given parameter, this is useful for when a command could
    take multiple different object types, otherwise it will use the parameters
    name.

    This should return a list that looks like:
    [('page/command', False)]

    :param f: The function to parse parameters for.
    :param doc: The pre-parsed documentation."""
    raw_arg_list = list(inspect.signature(f).parameters.items())
    if not raw_arg_list:
        return []
    if raw_arg_list[0][0] == 'self':
        raw_arg_list = raw_arg_list[1:]
    for item in list(raw_arg_list):
        name, param = item
        if not param.annotation:
            break
        if isinstance(param.annotation, type):
            if param.annotation.__name__ == 'CommandHandler':
                raw_arg_list.remove(item)
            elif param.annotation.__name__ == 'Character':
                raw_arg_list.remove(item)
        elif isinstance(param.annotation, str):
            if param.annotation == 'Character':
                raw_arg_list.remove(item)
            elif param.annotation == 'Cell':
                raw_arg_list.remove(item)
        else:
            break
    if not raw_arg_list:
        return []
    response = []
    for sig_val, doc_val in itertools.zip_longest(
            raw_arg_list, doc.get('params', [])):
        name = sig_val[0]
        if doc_val:
            name = '/'.join(doc_val)
        if sig_val[1].default == inspect._empty:
            name = f'<{name}>'
        else:
            name = f'[{name}]'
        response.append(name)
    return response


def command(f):
    """Wrapper for a function which is a command."""
    doc = _parse_documentation(f)
    doc_params = _parse_command_help_params(f, doc)
    setattr(f, '__command__', dict(func=f, doc_param=doc_params, **doc))
    return f


def autocomplete(obj: str):
    """Wrapper for a function which designates the a category of items available
    for autocompletion.

    :param obj: The object to handle autocompletion data for."""
    def _inner(f):
        setattr(f, '__autocomplete__', obj)
        return f
    return _inner


def aliases(f):
    """Wrapper for a function which provides aliases."""
    setattr(f, '__alias__', True)
    return f


class CommandHandler:
    """The CommandHandler handles all the sub command handlers within the game.
    This means each system in the game can be compartmentalised into a single
    file."""
    _handlers: List[Any]
    _character: 'Character'

    def __init__(self, character: 'Character'):
        self._handlers = []
        self._character = character

    def add_command_handler(self, handler: Any):
        """Adds a command handler.

        :param handler: The command handler."""
        self._handlers.append(handler)

    def remove_command_handler(self, handler: Type):
        """Removes all types of a given command handler.

        :param handler: The command handler."""
        self._handlers = [
            h for h in self._handlers
            if not isinstance(h, handler)
        ]

    async def handle_input(self, input: List[str]):
        """Invokes a command for the given input string."""
        if not input:
            return
        command_list = self._get_command_list_internal()
        if input[0].startswith('\\'):
            input[0] = input[0][1:]
            input = ['say'] + input
        known_aliases = self._get_alias_handlers()
        if input[0] in known_aliases:
            input = known_aliases[input[0]].split(' ') + input[1:]
        if input[0] not in command_list:
            closest = find_closest_match(input[0], command_list.keys())
            if closest[0]:
                await self._character.send_message(
                    'game', '@red@Unknown command, did you mean "@lbl@{}@red@"?@res@\n', closest[0])
            else:
                await self._character.send_message(
                    'game', '@red@Unable to find command@res@\n')
            return
        try:
            handler, command_data = command_list[input[0]]
            arguments = self._build_initial_argument_list(command_data["func"])
            await command_data['func'](handler, *(arguments + input[1:]))
        except TypeError as e:
            reg = re.compile(
                f'{command_data["func"].__qualname__}\\(\\) takes (from )?\\d+ (to \\d )?positional arguments but \\d+ were given')
            ureg = re.compile(
                f'{command_data["func"].__qualname__}\\(\\) missing \\d+ required positional argument: \'.+\''
            )
            mul_reg = re.compile(
                f'{command_data["func"].__qualname__}\\(\\) missing \\d+ required positional arguments: .+'
            )
            if reg.match(str(e)) or ureg.match(str(e)) or mul_reg.match(str(e)):
                await self._character.send_message('game', '@lre@Invalid command usage, type "@lbl@help {}@lre@" for information on this command. @res@\n', input[0])
            else:
                raise

    def _build_initial_argument_list(self, func: Callable):
        """Builds a list of arguments which are first needed to be passed into
        a function to work, these are based on the argument type and allow
        functions to be as basic as possible but accept the type they need."""
        raw_arg_list = list(inspect.signature(func).parameters.items())
        if not raw_arg_list:
            return []
        if raw_arg_list[0][0] == 'self':
            raw_arg_list = raw_arg_list[1:]
        args: List[Any] = []
        for name, param in raw_arg_list:
            if not param.annotation:
                break
            if isinstance(param.annotation, type):
                if param.annotation.__name__ == 'CommandHandler':
                    args.append(self)
                elif param.annotation.__name__ == 'Character':
                    args.append(self._character)
            elif isinstance(param.annotation, str):
                if param.annotation == 'Character':
                    args.append(self._character)
                elif param.annotation == 'Cell':
                    args.append(self._character._cell)
            else:
                break
        return args

    def get_suggestion(self, cmd: List[str], alternative=False):
        """Returns the current autocomplete for the given input, if there is an
        incomplete suggestion then it will return that suggestion.

        If the suggestions are complete then we'll return the next suggestion in
        the list.

        :param cmd: The input from the player given as a list.
        :param alternative: Whether to autocomplete to an alternative."""
        if not cmd or not cmd[0]:
            return ''
        valid_functions = {
            k: v[1] for k, v in self._get_command_list_internal().items()
            if k.startswith(cmd[0])}
        if not valid_functions:
            return ''
        name, fn = list(valid_functions.items())[0]
        if cmd[0] != name:
            if len(cmd) == 1:
                return name
            else:
                return ''
        if len(cmd) == 1:
            return ''
        params = fn.get('params', None)
        if not params:
            return ''
        if len(cmd) - 1 > len(params):
            return ''
        suggestion_funcs = self._get_autocomplete_handlers(
            params
            [len(cmd) - 2])
        raw_suggestion_list: List[str] = []
        suggestion_list: List[str] = []
        for handler, suggestion_func in suggestion_funcs:
            base_arguments = self._build_initial_argument_list(suggestion_func)
            raw_suggestion_list.extend(
                suggestion_func(
                    handler, *(base_arguments + [cmd])))
            if alternative:
                suggestion_list = [
                    s[1: -1]
                    if len(s) > 2 and s[0] == '"' and s[-1] == '"' else s
                    for s in raw_suggestion_list]
            else:
                suggestion_list = raw_suggestion_list
        raw_suggestion_list = list(OrderedDict.fromkeys(raw_suggestion_list))
        suggestion_list = list(OrderedDict.fromkeys(suggestion_list))
        if cmd[-1] not in suggestion_list:
            matching_suggestions = next((
                suggestion
                for suggestion in raw_suggestion_list
                if suggestion.startswith(cmd[-1])
            ), '')
            return ' '.join(cmd[:-1]) + ' ' + matching_suggestions
        if not alternative:
            return ''
        idx = suggestion_list.index(cmd[-1]) + 1
        if idx == len(suggestion_list):
            idx = 0
        return ' '.join(cmd[:-1]) + ' ' + raw_suggestion_list[idx]

    def _get_command_list_internal(self):
        """Returns the list of commands from all command handlers along with the
        handler it came from."""
        fns = {
            k: (handler, getattr(v, '__command__'))
            for handler in self._handlers
            for k, v in handler.__class__.__dict__.items()
            if getattr(v, '__command__', None) is not None
        }
        return fns

    def _get_autocomplete_handlers(self, obj: Iterable[str]):
        """Returns a list of autocomplete handlers for the given object type."""
        fns = [
            (handler, v)
            for handler in self._handlers
            for k, v in handler.__class__.__dict__.items()
            if getattr(v, '__autocomplete__', None) is not None and
            getattr(v, '__autocomplete__') in obj
        ]
        return fns

    def _get_alias_handlers(self):
        """Returns a list of alias providers."""
        fns = {
            alias: cmd
            for handler in self._handlers
            for k, v in handler.__class__.__dict__.items()
            if getattr(v, '__alias__', None)
            for alias, cmd in v(handler)
        }
        return fns
    
    def get_command(self, command: str):
        """Returns the command data for the given command."""
        fns = [
            getattr(v, '__command__')
            for handler in self._handlers
            for k, v in handler.__class__.__dict__.items()
            if getattr(v, '__command__', None) is not None
        ]
        fn = next(iter([f for f in fns if f['func'].__name__ == command]), None)
        print(fn)
        return fn

    def get_command_list(self):
        """Returns a list of all the commands."""
        fns = [
            getattr(v, '__command__')
            for handler in self._handlers
            for k, v in handler.__class__.__dict__.items()
            if getattr(v, '__command__', None) is not None
        ]
        fns.sort(key=lambda x: x['func'].__name__)
        return fns
