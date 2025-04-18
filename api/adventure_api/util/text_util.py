from collections import defaultdict
from typing import Dict, List, TypedDict

ADJECTIVE_ORDER = [
    'state'
]

class Noun(TypedDict):
    noun: str
    adjectives: Dict[str, str]

def get_noun_listings(noun_list: List[Noun], text_input: List[str]) -> List[Dict[str, List[Noun]]]:
    """Given a list of nouns and adjectives returns the autocomplete results
    for the given prefixes.

    This function should return a list of dictionaries where the key is the
    matched noun or adjective and the value is a list of items that match the
    prefix.
    """
    print(noun_list, text_input)
    if not text_input:
        return []
    
    grouped_adjectives = defaultdict(list)
    grouped_nouns_and_adjs = defaultdict(list)
    
    for item in noun_list:
        noun = item['noun']
        adjectives = item['adjectives']
        grouped_nouns_and_adjs[noun].append(item)
        
        for adj_value in adjectives.values():
            grouped_adjectives[adj_value].append(item)
            grouped_nouns_and_adjs[adj_value].append(item)
    
    for prefix in text_input[:-1]:
        if prefix not in grouped_adjectives:
            return []
        noun_list = grouped_adjectives[prefix]

    last_prefix = text_input[-1]
    result = []
    matched_keys = sorted(k for k in grouped_nouns_and_adjs if k.startswith(last_prefix))
    
    for key in matched_keys:
        result.append({key: grouped_nouns_and_adjs[key]})
    
    return result


if __name__ == '__main__':
    noun_list = [
        {'noun': 'gem', 'adjectives': {'color': 'red', 'size': 'small'}},
        {'noun': 'gem', 'adjectives': {'color': 'red', 'size': 'large'}},
        {'noun': 'gem', 'adjectives': {'color': 'blue', 'size': 'large'}},
        {'noun': 'gem', 'adjectives': {'color': 'black', 'size': 'small'}},
        {'noun': 'gear', 'adjectives': {'color': 'red', 'size': 'small'}},
        {'noun': 'apple', 'adjectives': {'color': 'green', 'size': 'small'}},
    ]

    # Example Queries
    # print(get_noun_listings(noun_list, ['g']))  # Matches 'gem', 'gear', 'green'
    # print(get_noun_listings(noun_list, ['re']))  # Matches 'red'
    print(get_noun_listings(noun_list, ['gre']))  # Matches 'apple'
    print(get_noun_listings(noun_list, ['green', 'a']))  # Matches 'apple'
    print(get_noun_listings(noun_list, ['apple', 'gre']))  # Matches 'apple'

    noun_list = [
        {'noun': 'rabbit', 'adjectives': {'state': 'dead'}},
    ]
    print(get_noun_listings(noun_list, ['rabbit']))
    print(get_noun_listings(noun_list, ['dea']))
    print(get_noun_listings(noun_list, ['dead', 'r']))
    print(get_noun_listings(noun_list, ['dead', 'r']))
    print(get_noun_listings(noun_list, ['rabbit', 'de']))
