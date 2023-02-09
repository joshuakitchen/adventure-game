from typing import TYPE_CHECKING
from .base import command
from ..world import World

if TYPE_CHECKING:
    from ..character import Character


class ChatCommands:
    """Handles chatting within the game."""

    @command
    async def say(self, c: 'Character', *message):
        """Says something in the chat, currently only the global chat channel
        exists."""
        if not c._cell:
            return
        message_str = ' '.join(message)
        await World.send_to_all('chat', '@lgr@{}@res@: {}\n', c._name, message_str)
