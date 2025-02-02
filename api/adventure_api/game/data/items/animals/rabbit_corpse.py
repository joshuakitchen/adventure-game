import random
from typing import TYPE_CHECKING, List
from game.item import Item

if TYPE_CHECKING:
    from game.character import Character
    from game.cell import Cell

on_survey = {
    'default': {
        'singular': [
            "You find a @yel@dead rabbit@res@. It looks like it was killed recently.",
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
    """sentence to add to the surveying of the general area if a rabbit corpse is found in the area."""
    choices = []
    if len(item) == 1:
        choices += on_survey['default']['singular']
    elif len(item) == 2:
        choices += on_survey['default']['plural']
    else:
        choices += on_survey['default']['group']
    return random.choice(choices)


rabbit_corpse_definition = {
    'id': 'rabbit_corpse',
    'name': 'Rabbit Corpse',
    'description': {
        'base': 'A @yel@dead rabbit@res@. It looks like it was killed recently.',
    },
    'command_name': 'rabbit_corpse',
    'slots_taken': 3,
    'qualifiers': {},
    'on_survey': on_survey_fn
}

Item.register_item(rabbit_corpse_definition)
