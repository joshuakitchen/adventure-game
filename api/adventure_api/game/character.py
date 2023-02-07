import json
from fastapi import WebSocket
from typing import Any, Dict, Optional
from ..config import get_conn

INTRODUCTION_TEXT = ''' _  _            _     _ _   _
| \\| |_  _ _ __ (_)_ _(_) |_| |_
| .` | || | '  \\| | '_| |  _| ' \\
|_|\\_|\\_, |_|_|_|_|_| |_|\\__|_||_|
      |__/


Welcome to the world of Nymirith.

Type "begin" followed by your character name to start.
\n\n'''


class Character:
    """The Character class handles the data for a single character within the
    game, this represents a person connected through a WebSocket."""
    _id: str
    _ws: WebSocket
    _state: str
    _name: Optional[str]

    def __init__(self, id: str, ws: WebSocket):
        """Constructs the Character

        :param id: The user id.
        :param ws: The websocket the user is connected with."""
        self._id = id
        self._ws = ws
        self._state = 'intro'
        self._name = None
        self.load_character()

    async def handle_login(self):
        """Handles the character entering the world, this will take place just
        after the WebSocket connection and should provide either an introduction
        for new players, or an update for old players."""
        if self._state == 'intro':
            await self.send_message('game', INTRODUCTION_TEXT, 'test')

    async def send_message(self, type: str, message: str, *args, **kwargs):
        """Sends a message to the Characters connected WebSocket.

        :param type: The type of request to send (game,chat,stats,error).
        :param message: The message to send.
        :param *args: Formats the message with the given arguments.
        :param **kwargs: Formats the message with the given kwargs."""
        await self._ws.send_json(
            dict(
                type=type,
                data=message.format(
                    *args,
                    **kwargs)))

    def to_json(self) -> str:
        """Converts the character to JSON for saving."""
        return json.dumps(dict(state=self._state, name=self._name))

    def from_json(self, raw_data: str):
        """Converts the character back from JSON for loading.

        :param data: The data as a string."""
        data: Dict[str, Any] = json.loads(raw_data)
        self._state = data.get('state', 'intro')
        self._name = data.get('name', None)

    def load_character(self):
        """Loads the character using the current database driver."""
        driver, conn = get_conn()
        if driver == 'sqlite':
            pass  # TODO: implement the sqlite driver
        elif driver == 'postgres':
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT state FROM users WHERE id = %s', [self._id])
                data = cur.fetchone()
            if data and data[0]:
                self.from_json(data[0])

    def save_character(self):
        """Saves the character using the current database driver."""
        driver, conn = get_conn()
        if driver == 'sqlite':
            pass  # TODO: implement the sqlite driver
        elif driver == 'postgres':
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE users SET state = %s WHERE id = %s', [
                        self.to_json(), self._id])
                conn.commit()
