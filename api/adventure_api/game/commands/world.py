from typing import List, Optional, TYPE_CHECKING
from .base import aliases, autocomplete, command, CommandHandler
from ..world import World

if TYPE_CHECKING:
    from ..cell import Cell
    from ..character import Character


IMMOVABLE_BIOMES = ['sea', 'mountain']


class WorldCommands:
    """Command handler for commands which interact with the world and areas
    within that world."""

    @command
    async def survey(self, c: 'Character', cell: 'Cell'):
        """Surveying maps the immediate surrounding area and shows it the player.

        :command_summary: Maps the surrounding area."""
        minimap = ""

        for z in range(5):
            for x in range(9):
                cx = c._x + x - 4
                cz = c._z + z - 2
                if cx == c._x and cz == c._z:
                    minimap = minimap + '@lre@@@res@'
                else:
                    minimap = minimap + World.get_cell(cx, cz).get_icon()
            minimap = minimap + '\n'
        entity_names: List[str] = [f'@red@{e.name}@res@' for e in cell._enemies]
        await c.send_message('game', 'You survey the surrounding area.\n{}\nYou can see:\n{}\n', minimap, '\n'.join(entity_names))

    @command
    async def scavenge(self, character: 'Character'):
        """Scavenging is an action which depending on what kind of area you are
        in, generates items. It is useful for getting essential items but won't
        get you anything too rare.

        :command_summary: Scavenges the local are for items."""
        await character.set_action('scavenge')

    @command
    async def stop(self, character: 'Character'):
        """Stops the current action which is being taken.

        :command_summary: Stops the current action."""
        await character.set_action(None)

    @command
    async def go(self, c: 'Character', direction: str):
        """Moves the player to an accompanying node according to direction.

        The player cannot move onto sea or mountain nodes.

        :command_summary: Moves the player in the direction specified.
        :command_param_type direction: direction"""
        available_directions: List[str] = []
        if World.get_cell(c._x - 1, c._z)._biome not in IMMOVABLE_BIOMES:
            available_directions.append('west')
        if World.get_cell(c._x + 1, c._z)._biome not in IMMOVABLE_BIOMES:
            available_directions.append('east')
        if World.get_cell(c._x, c._z - 1)._biome not in IMMOVABLE_BIOMES:
            available_directions.append('north')
        if World.get_cell(c._x, c._z + 1)._biome not in IMMOVABLE_BIOMES:
            available_directions.append('south')
        if direction not in available_directions:
            await c.send_message('game', '@red@You are unable to go in that direction.@res@\n')
            return
        ox, oz = c._x, c._z
        if direction == 'west':
            c._x = c._x - 1
        elif direction == 'east':
            c._x = c._x + 1
        elif direction == 'north':
            c._z = c._z - 1
        elif direction == 'south':
            c._z = c._z + 1
        World.unload_cell(ox, oz, c)
        World.load_cell(c._x, c._z, c)
        c._target = None
        await self.survey(c, c._cell)

    @command
    async def inspect(self, c: 'Character', cell: 'Cell', target, ordinal: Optional[int] = None):
        """Inspects the given target.

        :command_summary: Inspects the given target.
        :command_param_type: target"""
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
        if len(targets) > 1 and ordinal is None:
            await c.send_message('game', '@red@Multiple targets found, please specify which using attack [enemy] [number]@res@\n')
            return
        if ordinal is None:
            ordinal_int = 0
        try:
            target = targets[ordinal_int]
        except IndexError:
            await c.send_message('game', '@red@Target could not be found.@res@\n')
        await c.send_message('game', '{} It looks {}.\n', target.description, target.damage_state)

    @autocomplete('direction')
    def autocomplete_direction(self, c: 'Character',
                               input: List[str]) -> List[str]:
        """Autocompletes the direction which the available surrounding cells
        that can be moved to."""
        available_directions: List[str] = []
        if World.get_cell(c._x - 1, c._z)._biome not in IMMOVABLE_BIOMES:
            available_directions.append('west')
        if World.get_cell(c._x + 1, c._z)._biome not in IMMOVABLE_BIOMES:
            available_directions.append('east')
        if World.get_cell(c._x, c._z - 1)._biome not in IMMOVABLE_BIOMES:
            available_directions.append('north')
        if World.get_cell(c._x, c._z + 1)._biome not in IMMOVABLE_BIOMES:
            available_directions.append('south')
        return available_directions

    @aliases
    def alias_provider(self):
        return (('n', 'go north'), ('s', 'go south'),
                ('e', 'go east'), ('w', 'go west'), ('move', 'go'))
