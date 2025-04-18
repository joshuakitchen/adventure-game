import os
import importlib
import pathlib
import logging
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from game.character import Character

logger = logging.getLogger(__name__)

LOCAL_PATH = pathlib.Path(__file__).parent
PERSONAL_PRONOUNS = ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'one']

def verb(verb: str):
    def decorator(func):
        SentenceHandler.VERB_BAG.append((verb, func))
        return func
    return decorator

class SentenceParseError(Exception):
    """Raised when the sentence cannot be parsed."""
    pass

class InvalidPronounError(SentenceParseError):
    """Raised when the pronoun is invalid."""
    pass

class UnknownVerbError(SentenceParseError):
    """Raised when the verb is not recognized."""
    pass

class InvalidTargetError(SentenceParseError):
    """Raised when the target is invalid."""
    pass

class SentenceContext:
    """Holds the current sentences context."""
    sentence: str
    words: List[str]
    idx: int
    pronoun: Optional[str]
    next_context: Optional['SentenceContext']
    prev_context: Optional['SentenceContext']

    def __init__(self, sentence, prev_context: Optional['SentenceContext'] = None):
        self.sentence = sentence
        self.words = [word.lower() for word in sentence.split()]
        self.idx = 0
        self.pronoun = None
        self.next_context = None
        self.prev_context = prev_context
    
    def next_word(self) -> str:
        if self.is_end:
            return None
        self.idx += 1
        return self.words[self.idx - 1]

    @property
    def is_end(self):
        return self.idx == len(self.words)


class SentenceHandler:
    """The sentence handler parses input from the user and returns with the
    command that should be executed."""
    VERB_BAG: List[Tuple[str, callable]] = []

    def __init__(self):
        raise NotImplementedError("This class should not be instantiated.")

    @staticmethod
    async def parse_sentence(c: 'Character', sentence: str) -> str:
        """Parses the sentence and returns the command that should be executed
        by the game."""
        ctx = SentenceContext(sentence)
        words = ctx.words

        if words[ctx.idx] in ['im', 'i\'m']:
            ctx.pronoun = 'i'
            ctx.words[ctx.idx] = 'i'
            ctx.words.insert(ctx.idx + 1, 'am')
        if words[ctx.idx] in PERSONAL_PRONOUNS:
            if words[ctx.idx] == 'i':
                ctx.pronoun = 'i'
                ctx.idx += 1
            elif words[ctx.idx] in ['you']:
                raise InvalidPronounError("You cannot use the pronoun 'you', you are roleplaying as the character.")
            elif words[ctx.idx] in ['he', 'she', 'it', 'we', 'they']:
                raise InvalidPronounError("You cannot make decisions for other characters.")
            elif words[ctx.idx] in ['one']:
                raise InvalidPronounError("You cannot use the pronoun 'one', you are roleplaying as the character.")
            else:
                raise InvalidPronounError(f"Invalid pronoun: {words[ctx.idx]}")
        else:
            ctx.pronoun = 'i'
        
        verb = words[ctx.idx]

        if verb not in [v[0] for v in SentenceHandler.VERB_BAG]:
            raise UnknownVerbError(f"You sadly don't know how to '{verb}', if you believe this is a mistake please submit a bug report.")
        
        for v in SentenceHandler.VERB_BAG:
            if v[0] == verb:
                ctx.idx += 1
                return await v[1](c, ctx)

    @staticmethod
    def load_terms():
        """Loads all the terms from the verbs directory."""
        for root, _, files in os.walk(os.path.join(LOCAL_PATH, 'words')):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    path = os.path.join(root, file)[len(str(LOCAL_PATH)):]
                    path = path.replace(os.path.sep, '.')
                    path = path.replace('.py', '')
                    logging.info(f'loaded terms from {path}')
                    importlib.import_module(f'{__package__}{path}', package=__package__)
