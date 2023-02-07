import asyncio
from typing import Any, ClassVar, List
from .character import Character


class World:
    """The World is an instance which contains all the players currently
    connected to this world."""
    _characters: ClassVar[List[Character]]

    @classmethod
    async def send_to_all(cls, type: str, message: str, *args, **kwargs):
        """Sends a message to all the players in the world.

        :param type: The message type.
        :param message: The message to send.
        :param *args: The arguments for formatting.
        :param **kwargs: The arguments for formatting."""
        await asyncio.gather(*[character.send_message(type, message, *args, **kwargs) for character in cls._characters])

    @classmethod
    def add_player(cls, character: Character):
        """Adds a character to the world pool

        :param character: The character to add."""
        cls._characters.append(character)

    @classmethod
    def remove_player(cls, character: Character):
        """Removes a character from the world pool.

        :param character: The character to remove."""
        cls._characters.remove(character)


World._characters = []
