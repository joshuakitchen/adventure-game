from binascii import hexlify
import textdistance
import time
import os
import random
from typing import List

_id_ord = random.randint(0, 0xffff)


def generate_id(e_type: int) -> str:
    global _id_ord
    _id_ord = (_id_ord + 1) % 0xffff
    return ''.join([
        hex(int(time.time()))[2:],
        hexlify(os.urandom(2)).decode('utf-8'),
        hex(_id_ord)[2:].rjust(2, '0')[:4],
        hex(e_type)[2:].rjust(2, '0')[:2]
    ])

def min_distance_threshold(word_len):
    if word_len <= 3:
        return 1
    elif word_len <= 6:
        return 2
    else:
        return 3

def find_closest_match(input_word: str, choices: List[str]) -> str:
    """Finds the closest matching word in a list of choices.
    
    :param input_word: The word to match.
    :param choices: The list of choices to match against.
    
    :return: The closest matching word and the distance as a tuple."""
    best_match = None
    best_distance = 999

    for choice in choices:
        min_dist = min_distance_threshold(len(choice))
        distance = textdistance.damerau_levenshtein.distance(input_word, choice)
        if distance < best_distance and distance <= min_dist:
            best_distance = distance
            best_match = choice
    
    return (best_match, best_distance)
    

from .xp import EXP_TABLE
