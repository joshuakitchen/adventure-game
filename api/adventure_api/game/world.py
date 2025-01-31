import asyncio
from datetime import datetime
from typing import Any, ClassVar, List, Tuple, TYPE_CHECKING
from .cell import Cell

if TYPE_CHECKING:
    from .character import Character


class World:
    """The World is an instance which contains all the players currently
    connected to this world."""
    _characters: ClassVar[List['Character']]
    _awaiting_characters: ClassVar[List[Tuple['Character', datetime]]]
    _loaded_cells: ClassVar[List[Cell]]

    @classmethod
    async def tick(cls):
        """Called each tick (600ms), applies different functions which could be
        useful in the game world."""
        for cell in cls._loaded_cells:
            await cell.tick()
        for character in cls._awaiting_characters:
            if (datetime.now() - character[1]).total_seconds() > 30:
                cls._awaiting_characters.remove(character)
                if character._cell:
                    cls.unload_cell(character._x, character._z, character)
                character.save_character()

    @classmethod
    def load_cell(cls, x: int, z: int, character: 'Character'):
        """Loads a cell and adds the character to it, this ensures players can
        all see and interact with eachother and entities within the same cell.

        :param x: The x coordinate of the cell.
        :param z: The z coordinate of the cell.
        :param character: The character."""
        for cell in cls._loaded_cells:
            if cell._x == x and cell._z == z:
                if character not in cell._characters:
                    cell._characters.append(character)
                return cell
        cell = Cell(x, z)
        cell._characters.append(character)
        cls._loaded_cells.append(cell)
        return cell

    @classmethod
    def unload_cell(cls, x: int, z: int, character: 'Character'):
        """Removes a character from a cell and if the cell is now empty, saves
        and unloads the cell to prevent cells from keeping in memory.

        :param x: The x coordinate of the cell.
        :param z: The z coordinate of the cell.
        :param character: The character."""
        loaded_cell = None
        for cell in cls._loaded_cells:
            if cell._x == x and cell._z == z:
                loaded_cell = cell
                break
        if not loaded_cell:
            return
        loaded_cell._characters.remove(character)
        if not loaded_cell._characters:
            cls._loaded_cells.remove(loaded_cell)

    @classmethod
    def get_cell(cls, x: int, z: int) -> Cell:
        """Gets a cell without loading it in, if it's loaded it will use the
        loaded cell, useful for generating map data."""
        for cell in cls._loaded_cells:
            if cell._x == x and cell._z == z:
                return cell
        return Cell(x, z)

    @classmethod
    async def send_to_all(cls, type: str, message: str, *args, **kwargs):
        """Sends a message to all the players in the world.

        :param type: The message type.
        :param message: The message to send.
        :param *args: The arguments for formatting.
        :param **kwargs: The arguments for formatting."""
        await asyncio.gather(*[character.send_message(type, message, *args, **kwargs) for character in cls._characters])

    @classmethod
    def add_player(cls, character: 'Character'):
        """Adds a character to the world pool

        :param character: The character to add."""
        for awaiting_character in cls._awaiting_characters:
            if awaiting_character[0]._id == character._id:
                cls._awaiting_characters.remove(awaiting_character)
                break
        if character not in cls._characters:
            cls._characters.append(character)

    @classmethod
    def remove_player(cls, character: 'Character'):
        """Removes a character from the world pool.

        :param character: The character to remove."""
        if character in cls._characters:
            cls._characters.remove(character)
        cls._awaiting_characters.append((character, datetime.now()))
    
    @classmethod
    def get_player_by_id(cls, id: int, awaiting=False) -> 'Character':
        """Gets a player by their id.

        :param id: The id of the player.
        :param awaiting: Whether to include awaiting characters."""
        if awaiting:
            for character in cls._awaiting_characters:
                if character[0]._id == id:
                    return character[0]
        for character in cls._characters:
            if character._id == id:
                return character
    
    @classmethod
    def get_player(cls, name: str, awaiting=False) -> 'Character':
        """Gets a player by their name.

        :param name: The name of the player.
        :param awaiting: Whether to include awaiting characters."""
        if awaiting:
            for character in cls._awaiting_characters:
                if character[0]._name == name:
                    return character
        for character in cls._characters:
            if character._name == name:
                return character
        return None


World._characters = []
World._awaiting_characters = []
World._loaded_cells = []
