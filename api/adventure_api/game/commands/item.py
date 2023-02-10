from .base import autocomplete, command
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..character import Character


class ItemCommands:

    @command
    async def inventory(self, c: 'Character'):
        """Checks your current inventory.

        :command_summary: Check your inventory."""
        if not c.inventory:
            await c.send_message('game', 'You have nothing in your inventory with {} free slots.\n', c.free_slots)
            return
        inventory_list = '\n'.join(
            [f'@yel@{i["name"]}@res@' for i in c.inventory])
        await c.send_message('game', 'You check your inventory and find:\n{}\n\nYou have {} free slots left.\n', inventory_list, c.free_slots)

    @command
    async def drop(self, c: 'Character', item: str):
        """Drops an item from your inventory.

        :command_summary: Drops an item from your inventory.
        :command_param_type item: inventory"""
        i_idx = -1
        for idx, i in enumerate(c.inventory):
            if i['name'] == item:
                i_idx = idx
                break
        if i_idx == -1:
            await c.send_message('game', 'You don\'t have a @yel@{}@res@.\n', item)
            return
        c.remove_item_at(i_idx)
        await c.send_message('game', 'You drop the @yel@{}@res@\n', item)

    @autocomplete('inventory')
    def autocomplete_inventory(self, c: 'Character', *inputs: str):
        return [
            f'"{i["name"]}"' if " " in i['name'] else i['name']
            for i in c.inventory
        ]
