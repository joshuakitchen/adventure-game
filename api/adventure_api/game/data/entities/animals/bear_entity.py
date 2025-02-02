import random
from typing import TYPE_CHECKING, List
from game.enemy import Enemy, register_enemy

if TYPE_CHECKING:
    from game.cell import Cell
    from game.character import Character

on_entry = {
    "forest": [
        "A @red@bear@res@ pushes through the dense foliage, its powerful form displacing branches as it moves.",
        "The crack of a tree limb breaking signals the arrival of a @red@bear@res@, its deep growl rumbling through the forest.",
        "A @red@bear@res@ emerges from the thick underbrush, its nose twitching as it scents the air.",
        "You hear the slow, deliberate steps of a @red@bear@res@ before it comes into view, sniffing at the base of a tree.",
        "Leaves and twigs crunch beneath the heavy paws of a @red@bear@res@ as it makes its way into the area."
    ],
    "plains": [
        "A @red@bear@res@ lumbers across the open plains, its powerful limbs moving with surprising ease.",
        "The distant shape of a @red@bear@res@ grows closer, its heavy footfalls audible as it nears.",
        "A @red@bear@res@ emerges from the tall grass, shaking loose stray stalks from its fur.",
        "You see a @red@bear@res@ sniffing at the wind, testing the air before making its way forward.",
        "A deep, guttural huff announces the presence of a @red@bear@res@ as it strides into the area."
    ],
    "default": [
        "A @red@bear@res@ lumbers into the area, its heavy steps leaving deep imprints.",
        "You hear the snapping of branches as a @red@bear@res@ forces its way forward.",
        "A @red@bear@res@ emerges from the shadows, sniffing the air with a low grunt.",
        "The ground seems to tremble slightly as a @red@bear@res@ strides in, its massive form imposing.",
        "A @red@bear@res@ lets out a deep huff before settling into the area, surveying its surroundings."
    ]
}


on_survey = {
    "forest": {
        "singular": [
            "A @red@bear@res@ leans against a tree, its claws raking against the bark.",
            "You catch sight of a @red@bear@res@ moving slowly between the trees, its powerful frame blending with the shadows.",
            "The air is filled with the low, rumbling breath of a @red@bear@res@ resting near a fallen log.",
            "A @red@bear@res@ roots around the underbrush, searching for something unseen."
        ],
        "plural": [
            "The sound of heavy footfalls reveals two @red@bears@res@ moving through the forest, their deep grunts echoing.",
            "A pair of @red@bears@res@ claw at a rotting tree stump, tearing at the bark in search of insects.",
            "The rustling of leaves parts to reveal two @red@bears@res@ lumbering forward, their eyes scanning the area.",
            "Two @red@bears@res@ linger in the clearing, their forms massive against the towering trees."
        ],
        "group": [
            "A group of @red@bears@res@ roam through the forest, their sheer presence enough to make the area feel smaller.",
            "The low growls of multiple @red@bears@res@ mix with the sounds of snapping twigs as they shift through the trees.",
            "You hear the occasional huff and shuffle as several @red@bears@res@ move between the thick trunks.",
            "The undergrowth trembles slightly under the weight of a gathering of @red@bears@res@."
        ]
    },
    "plains": {
        "singular": [
            "A @red@bear@res@ stands on its hind legs, surveying the horizon before dropping back to all fours.",
            "The tall grass sways as a @red@bear@res@ moves through it, only parts of its massive frame visible.",
            "You see a @red@bear@res@ digging at the dirt, its claws kicking up small tufts of grass.",
            "A @red@bear@res@ paces slowly, watching the area with careful, deliberate movements."
        ],
        "plural": [
            "A pair of @red@bears@res@ roam the plains, their lumbering steps causing the ground to shake slightly.",
            "Two @red@bears@res@ sit near a patch of exposed rock, their heavy breaths visible in the cool air.",
            "The presence of two @red@bears@res@ is unmistakable, their dark shapes shifting against the open landscape.",
            "A deep growl breaks the silence as two @red@bears@res@ interact, their movements slow but powerful."
        ],
        "group": [
            "Several @red@bears@res@ move through the plains, their immense forms breaking the rhythm of the wind-swept grass.",
            "The heavy tread of multiple @red@bears@res@ can be felt as much as heard.",
            "A gathering of @red@bears@res@ stands together, their dark shapes a stark contrast to the golden plains.",
            "The low grumbles of a group of @red@bears@res@ fill the air, their presence undeniable."
        ]
    },
    "default": {
        "singular": [
            "A @red@bear@res@ stands tall, its gaze sweeping the area with slow intensity.",
            "You spot a @red@bear@res@ idly swiping at the ground, searching for food.",
            "A @red@bear@res@ lumbers forward, its thick fur shifting with each heavy step.",
            "The deep rumble of a @red@bear@res@ breathing fills the air as it surveys its surroundings."
        ],
        "plural": [
            "A pair of @red@bears@res@ forage nearby, their large forms moving with surprising grace.",
            "Two @red@bears@res@ watch each other warily before one turns its attention towards you.",
            "The heavy sounds of movement reveal two @red@bears@res@ shifting through the area.",
            "A couple of @red@bears@res@ grunt and huff, their thick fur bristling as they move about."
        ],
        "group": [
            "Several @red@bears@res@ roam the area, their presence undeniable.",
            "A gathering of @red@bears@res@ makes the ground seem smaller beneath their massive weight.",
            "The deep growls and shuffling of multiple @red@bears@res@ fill the air, each moving with purpose.",
            "A group of @red@bears@res@ seem to have claimed this space, their heavy forms dominating the landscape."
        ]
    }
}

async def on_bear_entry(self: Enemy, cell: 'Cell'):
    choices = []
    choices += on_entry.get(cell._biome, [])
    choices += on_entry['default']
    await cell.send_message('game', random.choice(choices))

def on_bear_survey(character: 'Character', entities: List[Enemy], cell: 'Cell', extended: bool=False):
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

bear_definition = {
    'id': 'bear',
    'collective_id': 'bears',
    'name': 'Bear',
    'description': [
        "A massive @red@bear@res@ stands before you, its fur matted and stained with dirt.",
    ],
    'hp': 24,
    'attack_timer': 5,
    'on_entry': on_bear_entry,
    'on_survey': on_bear_survey
}

register_enemy(bear_definition)
