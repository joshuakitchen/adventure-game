from typing import TYPE_CHECKING
from config import get_conn
from uuid import uuid4
from .base import command
from ..world import World

if TYPE_CHECKING:
    from ..character import Character


class ChatCommands:
    """Handles chatting within the game."""

    @command
    async def say(self, c: 'Character', *message):
        """Says something in the chat, currently only the global chat channel
        exists.
        
        :command_summary: Say something in the chat.
        :command_category: Interaction"""
        if not c._cell:
            return
        message_str = ' '.join(message)
        await World.send_to_all('chat', '@lgr@{}@res@: {}\n', c._name, message_str)
        
        driver, conn = get_conn()
        if driver == 'postgres':
            with conn.cursor() as cur:
                cur.execute('INSERT INTO chatlog (id, user_id, message) VALUES (%s, %s, %s)', [str(uuid4()), c._id, message_str])
            conn.commit()
