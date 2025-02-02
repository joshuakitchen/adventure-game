import random
from typing import TYPE_CHECKING, List
from game.enemy import Enemy, register_enemy

if TYPE_CHECKING:
    from game.cell import Cell
    from game.character import Character

on_entry = {
    "forest": [
        "A low growl rumbles through the dense woods as a @red@wolf@res@ emerges from the shadows.",
        "The snapping of a twig breaks the silence, and a @red@wolf@res@ steps into view, its eyes glinting.",
        "You hear the rustle of leaves, followed by the soft padding of paws—a @red@wolf@res@ prowls into the area.",
        "A @red@wolf@res@ slinks between the trees, barely making a sound as it surveys its surroundings.",
        "Golden eyes gleam in the dim light before a @red@wolf@res@ steps out from behind a thick tree trunk."
    ],
    "plains": [
        "A @red@wolf@res@ emerges from the tall grass, moving with deliberate caution.",
        "A chilling howl echoes across the plains as a @red@wolf@res@ appears on the horizon.",
        "You see a dark shape loping toward you—it's a @red@wolf@res@, scanning the area for prey.",
        "A sudden movement in the grass reveals a @red@wolf@res@ stalking silently through the open field.",
        "A @red@wolf@res@ trots confidently into the area, its powerful frame outlined against the sky."
    ],
    "default": [
        "A @red@wolf@res@ strides into the area, its gaze sharp and unyielding.",
        "You hear the soft crunch of paws on the ground before a @red@wolf@res@ appears.",
        "A @red@wolf@res@ emerges from the shadows, sniffing the air cautiously.",
        "The air feels tense as a @red@wolf@res@ steps into view, eyes gleaming.",
        "A @red@wolf@res@ surveys the area before padding forward with slow, deliberate steps."
    ]
}


on_survey = {
    "forest": {
        "singular": [
            "The faint crack of a branch betrays the presence of a @red@wolf@res@, watching from the undergrowth.",
            "A @red@wolf@res@ prowls between the trees, moving with quiet precision.",
            "You catch a glimpse of a @red@wolf@res@ lurking in the shadows, its piercing eyes locked onto you.",
            "A @red@wolf@res@ stands still in the distance, ears flicking as it listens to the sounds of the forest."
        ],
        "plural": [
            "The hushed padding of paws signals the presence of two @red@wolves@res@ moving through the woods.",
            "A pair of @red@wolves@res@ weave between the trees, their movements eerily silent.",
            "You see two @red@wolves@res@ watching from the undergrowth, their eyes glowing faintly in the dim light.",
            "A pair of @red@wolves@res@ slip through the forest, their forms barely visible against the dense foliage."
        ],
        "group": [
            "The forest feels tense as a pack of @red@wolves@res@ moves as one, their shapes shifting between the trees.",
            "A low chorus of growls and the glint of fangs reveal the presence of several @red@wolves@res@ nearby.",
            "A group of @red@wolves@res@ skulk through the shadows, their sharp eyes scanning the terrain.",
            "The presence of multiple @red@wolves@res@ fills the air with an unsettling stillness, broken only by the occasional crunch of leaves."
        ]
    },
    "plains": {
        "singular": [
            "A @red@wolf@res@ paces through the grass, moving with calculated grace.",
            "You spot a @red@wolf@res@ in the distance, its dark form barely distinguishable against the waving grass.",
            "A @red@wolf@res@ stands at the edge of the plains, scanning the horizon before slinking away.",
            "The wind carries the scent of a predator—a @red@wolf@res@ moves nearby."
        ],
        "plural": [
            "Two @red@wolves@res@ move in tandem through the plains, their coordinated steps betraying their pack instincts.",
            "A pair of @red@wolves@res@ stand side by side, their eyes tracking something unseen.",
            "The golden grass ripples as two @red@wolves@res@ stalk quietly through the field.",
            "A chilling howl in the distance is followed by the sight of two @red@wolves@res@ moving toward each other."
        ],
        "group": [
            "A pack of @red@wolves@res@ roams the open plains, their dark shapes moving like shadows.",
            "Several @red@wolves@res@ prowl the field, their movements quick and precise.",
            "A chorus of howls pierces the air as a group of @red@wolves@res@ spread out across the plains.",
            "The sight of multiple @red@wolves@res@ patrolling the area makes the land feel suddenly more hostile."
        ]
    },
    "default": {
        "singular": [
            "A @red@wolf@res@ stands motionless, its ears twitching as it listens.",
            "You catch sight of a @red@wolf@res@ moving with quiet confidence.",
            "A @red@wolf@res@ lingers at the edge of your vision, watching intently.",
            "The presence of a @red@wolf@res@ is unmistakable—its form shifting subtly as it moves."
        ],
        "plural": [
            "A pair of @red@wolves@res@ move together, their steps synchronized.",
            "Two @red@wolves@res@ prowl nearby, their eyes reflecting a quiet menace.",
            "You notice two @red@wolves@res@ standing close, their movements deliberate and cautious.",
            "A pair of @red@wolves@res@ watch from a distance, their forms blending into the surroundings."
        ],
        "group": [
            "Several @red@wolves@res@ pace the area, their movements calculated and precise.",
            "A gathering of @red@wolves@res@ spreads out, their attention shifting between you and the surroundings.",
            "The presence of multiple @red@wolves@res@ makes the air feel heavier, filled with silent tension.",
            "A pack of @red@wolves@res@ moves as one, their predatory instincts on full display."
        ]
    }
}

async def on_wolf_entry(self: Enemy, cell: 'Cell'):
    choices = []
    choices += on_entry.get(cell._biome, [])
    choices += on_entry['default']
    await cell.send_message('game', random.choice(choices))

def on_wolf_survey(character: 'Character', entities: List[Enemy], cell: 'Cell', extended: bool=False):
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

wolf_definition = {
    'id': 'wolf',
    'collective_id': 'wolves',
    'name': 'Wolf',
    'description': [
        'A large, grey wolf with piercing eyes.',
    ],
    'hp': 8,
    'attack_timer': 3,
    'on_entry': on_wolf_entry,
    'on_survey': on_wolf_survey
}

register_enemy(wolf_definition)
