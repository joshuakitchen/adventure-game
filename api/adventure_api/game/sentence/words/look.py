from typing import TYPE_CHECKING

from ..handler import SentenceContext, InvalidTargetError, verb

if TYPE_CHECKING:
    from game.character import Character

@verb('look')
async def look(c: 'Character', ctx: 'SentenceContext'):
    target = ctx.next_word()
    print(target)
    if target is None:
        raise InvalidTargetError("You may want to try looking at something, someone or just 'around'.")
    
    if target == 'around':
        await c.command_handler.handle_input(['survey'])
    
    return 'look', c, ctx
