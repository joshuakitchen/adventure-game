import random
from typing import TYPE_CHECKING, List
from game.enemy import Enemy, register_enemy
from game.item import Item

if TYPE_CHECKING:
    from game.cell import Cell
    from game.character import Character

on_entry = {
    'forest': [
        'A @red@rabbit@res@ hops into the dense forest, blending with the trees.',
        'You hear a rustling in the bushes and a @red@rabbit@res@ hops out.',
        'A @red@rabbit@res@ cautiously emerges from a burrow beneath the roots of an ancient tree.',
        'Leaves crunch underfoot as a @red@rabbit@res@ scampers into view, ears twitching.',
        'A flicker of movement among the ferns reveals a @red@rabbit@res@, pausing to sniff the air.',
        'Dappled sunlight catches a @red@rabbit@res@ as it bounds between mossy logs.'
    ],
    'plains': [
        'A @red@rabbit@res@ hops into the open plains, nibbling on grass.',
        'You hear a rustling in the grass and a @red@rabbit@res@ hops out.',
        'A @red@rabbit@res@ darts through the tall grass, vanishing for a moment before reappearing.',
        'A sudden gust of wind sends the grass rippling as a @red@rabbit@res@ dashes into the open.',
        'You spot a @red@rabbit@res@ perched on its hind legs, scanning the horizon before resuming its grazing.',
        'A pair of twitching ears poke above the grass before a @red@rabbit@res@ hops into view.'
    ],
    'default': [
        'You spot a new @red@rabbit@res@ hopping around.',
        'A @red@rabbit@res@ hops into the area.',
        'A @red@rabbit@res@ bounds into the area, its nose twitching curiously.',
        'You catch sight of a @red@rabbit@res@ hopping in from the distance.',
        'A @red@rabbit@res@ pauses, ears flicking, before continuing its path into the area.'
    ]
}

on_survey = {
    'forest': {
        'singular': [
            'You hear the rustling of leaves as a @red@rabbit@res@ hops between the undergrowth.',
            'A @red@rabbit@res@ sits motionless among the ferns, ears perked and alert.',
            'The crunch of twigs underfoot draws your attention to a @red@rabbit@res@ moving cautiously.',
            'A @red@rabbit@res@ darts between the trees, disappearing into the shadows for a moment.'
        ],
        'plural': [
            'The occasional thump of paws on soft earth reveals a pair of @red@rabbits@res@ darting through the brush.',
            'Two @red@rabbits@res@ weave between the roots of towering trees, kicking up leaves as they move.',
            'You spot two @red@rabbits@res@ nestled in a patch of moss, twitching their noses as they watch you.',
            'A brief scuffle in the undergrowth catches your ear, two @red@rabbits@res@ chase each other in a playful burst of energy.'
        ],
        'group': [
            'A handful of @red@rabbits@res@ skitter across the forest floor, kicking up fallen leaves.',
            'You hear a series of soft thumps as a group of @red@rabbits@res@ leap over exposed roots and brambles.',
            'The underbrush rustles with movement as several @red@rabbits@res@ scurry about, foraging among the fallen leaves.',
            'A few @red@rabbits@res@ dart into the shadows, only their twitching ears visible between the trees.'
        ]
    },
    'plains': {
        'singular': [
            'A @red@rabbit@res@ sits in the tall grass, barely visible as it watches you cautiously.',
            'The grass sways slightly before parting to reveal a @red@rabbit@res@ hopping through.',
            'A @red@rabbit@res@ stands on its hind legs, scanning the area before returning to nibbling on some wildflowers.',
            'A sudden rustling in the grass reveals a @red@rabbit@res@ bounding across the open field.'
        ],
        'plural': [
            'A pair of @red@rabbits@res@ chase each other in playful circles before disappearing into the grass.',
            'The wind carries the soft sounds of movement—two @red@rabbits@res@ are foraging nearby.',
            'You notice two @red@rabbits@res@ sitting close together, their ears flicking as they listen for danger.',
            'A blur of fur moves through the plains as two @red@rabbits@res@ dart between patches of tall grass.'
        ],
        'group': [
            'A group of @red@rabbits@res@ scatter at the slightest noise, their quick movements sending ripples through the grass.',
            'Several @red@rabbits@res@ are huddled near a small patch of wildflowers, nibbling quietly.',
            'The plains are alive with the subtle presence of @red@rabbits@res@, their movement barely visible in the swaying grass.',
            'A few @red@rabbits@res@ bound across the open field, their fur blending with the golden hues of the grass.'
        ]
    },
    'default': {
        'singular': [
            'A @red@rabbit@res@ is hopping around, its nose twitching as it sniffs the air.',
            'You hear soft footfalls as a @red@rabbit@res@ moves about the area.',
            'A lone @red@rabbit@res@ watches you cautiously, ears flicking at the slightest sound.',
            'The faint patter of paws alerts you to a @red@rabbit@res@ moving nearby.'
        ],
        'plural': [
            'A couple of @red@rabbits@res@ dart back and forth, occasionally pausing to groom their fur.',
            'You hear a series of soft thumps—two @red@rabbits@res@ are moving together through the area.',
            'Two @red@rabbits@res@ huddle close, their noses twitching as they inspect their surroundings.',
        ],
        'group': [
            'A few @red@rabbits@res@ are hopping about, their soft footfalls blending into the ambient noise.',
            'The occasional flick of an ear or rustle of fur hints at the presence of multiple @red@rabbits@res@ nearby.',
            'A cluster of @red@rabbits@res@ scurry about, their movements almost synchronised.',
            'The soft murmur of movement disturbs a gathering of @red@rabbits@res@ spread across the area.'
        ]
    }
}

async def on_rabbit_entry(self: Enemy, cell: 'Cell'):
    choices = []
    choices += on_entry.get(cell._biome, [])
    choices += on_entry['default']
    await cell.send_message('game', random.choice(choices))

def on_rabbit_survey(character: 'Character', entities: List[Enemy], cell: 'Cell', extended: bool=False):
    choices = []
    if len(entities) == 1:
        choices += on_survey[cell._biome]['singular']
        choices += on_survey['default']['singular']
    elif len(entities) == 2:
        choices += on_survey[cell._biome]['plural']
        choices += on_survey['default']['plural']
    else:
        choices += on_survey[cell._biome]['group']
        choices += on_survey['default']['group']
    return random.choice(choices)

async def on_rabbit_defeat(self: Enemy, character: 'Character', cell: 'Cell'):
    cell.add_item(['rabbit_corpse', {}])

rabbit_definition = {
    'id': 'rabbit',
    'collective_id': 'rabbits',
    'name': 'Rabbit',
    'description': [
        'A fluffy, white bunny with twitching nose. ',
        'Shy, brown-eared rabbit hopping along.',
        'A lop-eared cutie which nibbles grass.',
        'A small, fuzzy bunny with long ears, big eyes and soft fur.'
    ],
    'hp': 4,
    'attack_timer': 3,
    'on_entry': on_rabbit_entry,
    'on_survey': on_rabbit_survey,
    'on_defeat': on_rabbit_defeat
}

register_enemy(rabbit_definition)
