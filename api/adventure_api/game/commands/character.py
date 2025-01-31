from typing import List, Optional, TYPE_CHECKING
from .base import autocomplete, command, CommandHandler
from util.windows import generate_stats

if TYPE_CHECKING:
    from ..character import Character

class CharacterCommands:

    @command
    async def stats(self, character: 'Character') -> str:
        """Displays the character's stats.

        :command_summary: Display character stats.
        :command_category: Character"""
        stat_display = "Name: {}\nFaction: {}\n\n".format(character.name, character.faction);
        stat_display += "Constitution: {}/{}\n".format(character._hp, character._attributes["constitution"][0])
        stat_display += "Strength: {}\n".format(character._attributes["strength"][0])
        stat_display += "Dexterity: {}\n".format(character._attributes["dexterity"][0])
        stat_display += "Magic: {}\n\n".format(character._attributes["magic"][0])
        for skill in character._skills:
            stat_display += "{}: {}\n".format(skill, character._skills[skill][0])
        await character.send_message('game', stat_display)
    
    @command
    async def statbox(self, character: 'Character') -> str:
        """Displays the character's stats in a box.

        :command_summary: Display character stats in a box.
        :command_category: Character"""
        attrs = []
        attrs.append(f'Constitution: {character._attributes["constitution"][0]}')
        attrs.append(f'Strength: {character._attributes["strength"][0]}')
        attrs.append(f'Dexterity: {character._attributes["dexterity"][0]}')
        attrs.append(f'Magic: {character._attributes["magic"][0]}')
        skills = []
        for skill in character._skills:
            skills.append(f'{skill}: {character._skills[skill]}')
        stat_display = generate_stats(character.name, character.faction, [], attrs, skills)
        await character.send_message('game', stat_display)
