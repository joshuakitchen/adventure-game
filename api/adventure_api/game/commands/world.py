import textwrap
import random
from typing import List, Optional, TYPE_CHECKING
from .base import aliases, autocomplete, command, CommandHandler
from ..enemy import Enemy
from ..world import World
from ..item import Item

if TYPE_CHECKING:
    from ..cell import Cell
    from ..character import Character


IMMOVABLE_BIOMES = ['sea', 'mountain']

SURVEY_MESSAGES = [
    "You take a moment to observe your surroundings.",
    "You scan the area, taking in the details.",
    "You glance around, looking for anything of interest.",
    "You carefully examine the landscape.",
    "You take in your surroundings, noting any movement.",
    "You pause to get a better sense of the area.",
    "You look around, searching for anything unusual.",
    "You study the environment, watching for signs of life.",
    "You assess the area, noting anything of importance."
]

class WorldCommands:
    """Command handler for commands which interact with the world and areas
    within that world."""

    @command
    async def survey(self, c: 'Character', cell: 'Cell'):
        """Surveying maps the immediate surrounding area and shows it the player.

        :command_summary: Maps the surrounding area.
        :command_category: Movement"""
        output = random.choice(SURVEY_MESSAGES) + ' '
        output += cell.description.replace(',', '') + ' '

        if cell.enemies:
            enemy_types = {}
            for e in cell.enemies:
                if e.name in enemy_types:
                    enemy_types[e.name] += [e]
                else:
                    enemy_types[e.name] = [e]

            for enemies in enemy_types.values():
                output += enemies[0].data['on_survey'](c, enemies, cell) + '\n'
        else:
            output += random.choice(cell.data['empty']) + '\n'
        
        if cell.items:
            item_types = {}
            for i in cell._items:
                if i[0] in item_types:
                    item_types[i[0]] += [i]
                else:
                    item_types[i[0]] = [i]
            
            for item in item_types.values():
                item_type = item[0][0]
                if 'on_survey' in Item.get_item_data(item_type):
                    output += Item.get_item_data(item_type)['on_survey'](c, item, cell) + '\n'

        output += '\n'

        output = textwrap.fill(output, 80) + '\n'

        biome_map = ''
        population_map = ''

        for z in range(5):
            for x in range(9):
                cx = c._x + x - 4
                cz = c._z + z - 2
                l_cell = World.get_cell(cx, cz)
                population_map = population_map + l_cell.population_icon
                if cx == c._x and cz == c._z:
                    biome_map = biome_map + '@lre@@@res@'
                else:
                    biome_map = biome_map + l_cell.biome_icon
            biome_map = biome_map + '\n'
            population_map = population_map + '\n'
        map_display = ''
        for bm, pm in zip(biome_map.split('\n'), population_map.split('\n')):
            map_display = map_display + bm + ' ' + pm + '\n'
        output += f'\n{map_display}'
        await c.send_message('game', output)

    @command
    async def pickup(self, c: 'Character', item: str):
        """Picks up an item from the local area.

        :command_summary: Picks up an item from the local area.
        :command_param_type item: item
        :command_category: Interaction"""
        i_idx = -1
        for idx, i in enumerate(c._cell.items):
            if i['name'] == item:
                i_idx = idx
                break
        else:
            await c.send_message('game', '@red@Item could not be found.@res@\n')
            return
        i_item = c._cell._items.pop(i_idx)
        c.add_item(i_item[0], i_item[1])
        await c.send_message('game', 'You pick up the @yel@{}@res@\n', item)

    @command
    async def scavenge(self, character: 'Character'):
        """Scavenging is an action which depending on what kind of area you are
        in, generates items. It is useful for getting essential items but won't
        get you anything too rare.

        :command_summary: Scavenges the local are for items.
        :command_category: Interaction"""
        await character.set_action('scavenge')

    @command
    async def stop(self, character: 'Character'):
        """Stops the current action which is being taken.

        :command_summary: Stops the current action.
        :command_category: Interaction"""
        await character.set_action(None)

    @command
    async def go(self, c: 'Character', direction: str):
        """Moves the player to an accompanying node according to direction.

        The player cannot move onto sea or mountain nodes.

        :command_summary: Moves the player in the direction specified.
        :command_param_type direction: direction
        :command_category: Movement"""
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
        c._cell = World.load_cell(c._x, c._z, c)
        c._target = None
        await self.survey(c, c._cell)

    @command
    async def look(self, c: 'Character', cell: 'Cell', target, ordinal: Optional[int] = None):
        """Look at a target within the local area, look can target either
        specific entities or a collective of entites.

        If you are to look at a singular rabbit, specify "@lbl@look @red@Rabbit@res@", if there
        are multiple rabbits in the region use "@lbl@look @red@Rabbit@res@ 2" to specify the
        ordinal of the rabbit you wish to look at.

        If you are to look at a collective of rabbits, you can use "@lbl@look@res@ @red@rabbits@res@",
        this will give you more information than just surveying did, such as if
        any of them are injured.

        :command_summary: Looks at the given target and gives a description.
        :command_param_type target: look_target
        :command_param_type ordinal: target_ordinal
        :command_category: Interaction"""
        collective = Enemy.get_collective(target)
        if collective is not None:
            await c.send_message('game', '{}', collective['on_survey'](c, cell._enemies, cell, extended=True))
            return
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
    
    @autocomplete('item')
    def autocomplete_item(self, c: 'Character', *inputs: str):
        """Autocompletes the item which can be picked up from the local area."""
        return [
            f'"{i["name"]}"' if " " in i['name'] else i['name']
            for i in c._cell.items
        ]
    
    @autocomplete('look_target')
    def autocomplete_look_target(self, cell: 'Cell', *inputs: str):
        """Autocompletes the target which can be looked at in the local area."""
        targets = [e.name for e in cell._enemies]
        targets += list(set([e.data['collective_id'] for e in cell._enemies]))
        return targets

    @aliases
    def alias_provider(self):
        return (('n', 'go north'), ('s', 'go south'),
                ('e', 'go east'), ('w', 'go west'), ('move', 'go'))
