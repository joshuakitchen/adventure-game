import random
from typing import TYPE_CHECKING, List
from game.item import Item

if TYPE_CHECKING:
    from game.character import Character
    from game.cell import Cell

on_survey = {
    'killed_by_me': {
        'singular': [
            "Along the floor is the @yel@dead rabbit@res@ you killed.",
        ],
        'plural': [
            'Strewn about the floor are a couple of @yel@dead rabbits@res@ you killed.'
        ],
        'group': [
            'Strewn about the floor are several @yel@dead rabbits@res@ you killed.'
        ]
    },
    'default': {
        'singular': [
            "You spot the outline of a @yel@dead rabbit@res@.",
        ],
        'plural': [
            'There are a couple of @yel@dead rabbits@res@ here. They look like they were killed recently.'
        ],
        'group': [
            'There are several @yel@dead rabbits@res@ here. They look like they were killed recently.'
        ]
    }
}

def on_survey_fn(character: 'Character', item: List['Item'], cell: 'Cell'):
    """sentence to add to the surveying of the general area if a dead rabbit is found in the area."""
    choices = []
    if len(item) == 1:
        choices += on_survey['default']['singular']
    elif len(item) == 2:
        choices += on_survey['default']['plural']
    else:
        choices += on_survey['default']['group']
    return random.choice(choices)


dead_rabbit_definition = {
    'id': 'dead_rabbit',
    'name': 'Dead Rabbit',
    'description': {
        'base': 'A @yel@dead rabbit@res@. It looks like it was killed recently.',
    },
    'noun': 'rabbit',
    'adjectives': {'state': 'dead'},
    'command_name': 'dead_rabbit',
    'slots_taken': 3,
    'qualifiers': {},
    'on_survey': on_survey_fn
}

Item.register_item(dead_rabbit_definition)
