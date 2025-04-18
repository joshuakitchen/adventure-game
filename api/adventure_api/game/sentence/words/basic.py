from typing import TYPE_CHECKING

from ..handler import SentenceContext, InvalidTargetError, SentenceHandler, verb

if TYPE_CHECKING:
    from game.character import Character

@verb('want')
async def want(c: 'Character', ctx: 'SentenceContext'):
    """Handles something or to do something."""
    target = ctx.next_word()
    if target is None:
        raise InvalidTargetError("Well, what do you want, perhaps you want to do something?")
    
    if target == 'to':
        verb = ctx.next_word()
        if verb is None:
            raise InvalidTargetError("You may want to try specifying what you want to do.")
        
        if verb == 'want':
            raise InvalidTargetError("You want to want something, what a novel concept.")
        else:
            if verb not in [v[0] for v in SentenceHandler.VERB_BAG]:
                raise InvalidTargetError(f"Sadly, despite wanting to, you don't know how to '{verb}', if you believe this is a mistake please submit a bug report.")
            
            for v in SentenceHandler.VERB_BAG:
                if v[0] == verb:
                    ctx.idx += 1
                    return await v[1](c, ctx)

        return
    
    return 'look', c, ctx

@verb('set')
async def set_(c: 'Character', ctx: 'SentenceContext'):
    """Sets something."""
    if ctx.words == ['set', 'input', 'command']:
        await c.set_setting('input', 'command')
        await c.send_message('game', 'You are now in command input mode, you should now type in commands to interact with the game.')
        return
    target = ctx.next_word()
    if target is None:
        raise InvalidTargetError("Well, what do you want to set?")
    
    return 'look', c, ctx