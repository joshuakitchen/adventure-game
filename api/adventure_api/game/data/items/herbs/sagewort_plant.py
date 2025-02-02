
from typing import TYPE_CHECKING
from game.item import Item

if TYPE_CHECKING:
    from game.character import Character

HEAL_VALUES = {
    'poor': 1,
    'average': 2,
    'good': 3,
    'excellent': 4
}

async def on_sagewort_eat(item, idx: int, character: 'Character'):
    character.remove_item_at(idx)
    character.health += HEAL_VALUES[item['qualifiers']['quality']]
    await character.send_message('game', 'You eat the @yel@sagewort@res@. It tastes bitter and earthy, but you feel a surge of energy.\nYou are now at {} health.\n', character.health)


sagewort_definition = {
    'id': 'sagewort',
    'name': '{quality} Sagewort',
    'description': {
        'base': 'A plant that is always green no matter the season.',
        'extra': {
            'quality==excellent': 'Its emitting a faint golden glow, pulsing with latent energy.',
            'quality==good': 'Its rich scent is reminiscent of fresh earth and morning dew.',
            'quality==average': 'The leaves are lush and full, a testament to its resilience.',
            'quality==poor': 'Its leaves are wilted and dull, as if struggling to survive.'
        }
    },
    'command_name': 'sagewort',
    'slots_taken': 1,
    'qualifiers': {
        'quality': ['poor', 'average', 'good', 'excellent']
    },
    "on_scavenge": {
      "quality==excellent": [
        ["add_exp", "herbalism", 2],
        ["message", "You find a sagewort plant that is in perfect condition. You carefully harvest it, gaining some experience in herbalism."]
      ],
      "quality==good": [
        ["add_exp", "herbalism", 1],
        ["message", "You find a sagewort plant that is healthy and vibrant. You harvest it, learning a bit about herbalism in the process."]
      ],
      "quality==average": [
        ["add_exp", "herbalism", 1],
        ["message", "You find a sagewort plant that is in decent shape. You harvest it, gaining a little experience in herbalism."]
      ],
      "quality==poor": [
        ["add_exp", "herbalism", 1],
        ["message", "You find a sagewort plant that is struggling to survive. You harvest it, but it doesn't teach you much."]
      ]
    },
    "on_eat": on_sagewort_eat
}

Item.register_item(sagewort_definition)
