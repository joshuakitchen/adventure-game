import itertools
from typing import Tuple, Iterable

STATS_START = """╒══════════════════════════════════════════════════════╕
│ @lgr@{name:^52}@res@ │
├──────────────────────────────────────────────────────┤
│ {faction:<52} │
├──────────────┬───────────────────┬───────────────────┤
│ General      │ Attributes        │ Skills            │
├──────────────┼───────────────────┼───────────────────┤
"""
STATS_LINE = """│ {:<12} │ {:<17} │ {:<17} │\n"""
STATS_END = '└──────────────┴───────────────────┴───────────────────┘'


def generate_stats(
        name: str, faction: str, general: Iterable[str],
        attributes: Iterable[str], skills: Iterable[str]):
    stats = STATS_START.format(name=name, faction=faction)
    for g, a, s in itertools.zip_longest(general, attributes, skills):
        stats = stats + STATS_LINE.format(g or '', a or '', s or '')
    stats = stats + STATS_END
    return stats
