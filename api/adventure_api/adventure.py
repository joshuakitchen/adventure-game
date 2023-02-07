import json
from fastapi import WebSocket
from .game.world import World


CHARACTERISTIC_LIST = [
    'race',
    'gender',
    'hair_length',
    'hair_colour',
    'eye_colour',
    'eye_shape']
CHARACTERISTIC_TO_PY = {
    'race': '_race',
    'gender': '_gender',
    'hair_length': '_hair_length',
    'hair_colour': '_hair_colour',
    'eye_shape': '_eye_shape',
    'eye_colour': '_eye_colour'
}
TYPES_LIST = {
    'race': ['human'],
    'gender': ['male', 'female'],
    'hair_length': ['short', 'medium', 'long'],
    'hair_colour': ['blonde', 'brown', 'red'],
    'eye_colour': ['brown', 'blue', 'green', 'grey'],
    'eye_shape': ['piercing']
}


class Character:
    _race: str
    _gender: str
    _hair_length: str
    _hair_colour: str
    _eye_shape: str
    _eye_color: str

    def __init__(self):
        self._race = 'human'
        self._gender = 'male'
        self._hair_length = 'long'
        self._hair_colour = 'red'
        self._eye_shape = 'piercing'
        self._eye_colour = 'green'

    def describe_self(self):
        return f'You are a {self._race} {self._gender}. You have {self._hair_length} {self._hair_colour} hair and {self._eye_shape} {self._eye_colour} eyes.'

    def to_json(self):
        return dict(
            race=self._race, gender=self._gender,
            hair=dict(length=self._hair_length, colour=self._hair_colour),
            eyes=dict(shape=self._eye_shape, colour=self._eye_colour))

    def from_json(self, data: dict):
        self._race = data['race']
        self._gender = data['gender']
        self._hair_length = data['hair']['length']
        self._hair_colour = data['hair']['colour']
        self._eye_shape = data['eyes']['shape']
        self._eye_colour = data['eyes']['colour']


class Adventure:
    _ws: WebSocket
    _user_id: str
    _state: str
    _x: int
    _z: int
    _character: Character

    def __init__(self, ws: WebSocket, user_id: str):
        self._ws = ws
        self._user_id = user_id
        self._state = 'start'
        self._character = Character()
        self._x = 50
        self._z = 50
        self.load()

    def get_intro(self):
        if self._state == 'start':
            return INTRODUCTION_TEXT.format(
                look=self._character.describe_self())
        elif self._state == 'character_creation':
            return f'Hello, you were in the middle of creating your character, here\'s how you look so far:\n{self._character.describe_self()}\n\n'
        return 'Welcome back\n'

    async def send_message(self, type: str, message: str, *args, **kwargs):
        await self._ws.send_text(json.dumps(dict(type=type, data=message.format(*args, **kwargs))))

    def save(self):
        with open(f'./data/saves/{self._user_id}.json', 'w') as f:
            f.write(
                json.dumps(
                    dict(
                        state=self._state,
                        x=self._x,
                        z=self._z,
                        character=self._character.to_json())))

    def load(self):
        try:
            with open(f'./data/saves/{self._user_id}.json', 'r') as f:
                data = json.loads(f.read())
                self._state = data['state']
                self._x = data['x']
                self._z = data['z']
                self._character.from_json(data['character'])
        except FileNotFoundError:
            pass
