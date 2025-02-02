from typing import List, Optional, TYPE_CHECKING
from .base import autocomplete, command, CommandHandler

if TYPE_CHECKING:
    from ..character import Character
    from ..cell import Cell


class CombatCommands:

    @command
    async def attack(self, c: 'Character', cell: 'Cell', target, ordinal=None):
        """Starts an attack against the target, attacks are automatic and happen
        every attack cycle.
        
        Type 'stop' to stop attacking the target, but be warned, the target may
        continue to attack you.

        :command_summary: Start attacking an enemy.
        :command_param_type target: target
        :command_param_type ordinal: target_ordinal
        :command_category: Combat"""
        if ordinal is not None:
            try:
                ordinal_int = int(ordinal) - 1
            except ValueError:
                await c.send_message('game', '@red@Ordinal must be a number.@res@\n')
                return
        targets = cell.find(target)
        if not targets:
            await c.send_message('game', '@red@Target could not be found.@res@\n')
            return
        if ordinal is None:
            ordinal_int = 0
        try:
            target = targets[ordinal_int]
        except IndexError:
            await c.send_message('game', '@red@Target could not be found.@res@\n')
        await c.start_attacking(target.id)

    @autocomplete('target')
    def autocomplete_target(self, cell: 'Cell', input: List[str]):
        """Autocompletion handler for the different targets available."""
        return [e.name.lower() for e in cell._enemies]

    @autocomplete('target_ordinal')
    def autocomplete_target_ordinal(self, cell: 'Cell', input: List[str]):
        """Attempts to auto-complete the targets ordinal."""
        targets = cell.find(input[1])
        return [str(i + 1) for i in range(len(targets))]
