
from game.item import Item

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
    }
}

Item.register_item(sagewort_definition)
