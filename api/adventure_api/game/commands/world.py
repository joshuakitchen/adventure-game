from typing import List, TYPE_CHECKING
from .base import command
from ..world import World

if TYPE_CHECKING:
    from ..cell import Cell
    from ..character import Character


class WorldCommands:
    """Command handler for commands which interact with the world and areas
    within that world."""

    @command
    async def survey(self, c: 'Character'):
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
        entity_names: List[str] = []
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
