from .base import autocomplete, command
from typing import List, TYPE_CHECKING
from ..item import Item

if TYPE_CHECKING:
    from ..character import Character


class ItemCommands:

    @command
    async def inventory(self, c: 'Character'):
        """Checks your current inventory.

        :command_summary: Check your inventory.
        :command_category: Inventory"""
        if not c.inventory:
            await c.send_message('game', 'You have nothing in your inventory with {} free slots.\n', c.free_slots)
            return
        inventory_list = '\n'.join(
            [f'@yel@{i["name"]}@res@' for i in c.inventory])
        await c.send_message('game', 'You check your inventory and find:\n{}\n\nYou have {} free slots left.\n', inventory_list, c.free_slots)

    @command
    async def drop(self, c: 'Character', item: str):
        """Drops an item from your inventory to the current cell.

        If you want to drop every item you can use the keyword 'all'.

        :command_summary: Drops an item from your inventory.
        :command_param_type item: inventory
        :command_category: Inventory"""
        if item == 'all':
            count = len(c.inventory)
            for i in range(count):
                c._cell.add_item(0)
                c.remove_item_at(0)
            
            await c.send_message('game', 'You drop all items in your inventory.\n')
            return
        i_idx = -1
        for idx, i in enumerate(c.inventory):
            if i['name'] == item:
                i_idx = idx
                break
        if i_idx == -1:
            await c.send_message('game', 'You don\'t have a @yel@{}@res@.\n', item)
            return
        inv_item = c._inventory[i_idx]
        c.remove_item_at(i_idx)
        c._cell.add_item(inv_item)
        await c.send_message('game', 'You drop the @yel@{}@res@\n', item)

    @command
    async def inspect(self, c: 'Character', item: str):
        """Inspects an item in your inventory.
        
        :command_summary: Inspects an item in your inventory.
        :command_param_type item: inventory
        :command_category: Inventory"""
        for i in c.inventory:
            if i['name'] == item:
                await c.send_message('game', 'You inspect the @yel@{}@res@ and find:\n{}\n', item, i['description'])
                return
        await c.send_message('game', 'You don\'t have a @yel@{}@res@.\n', item)
    
    @command
    async def eat(self, c: 'Character', item: str):
        """Eats an item in your inventory.
        
        :command_summary: Eats an item in your inventory.
        :command_param_type item: inventory
        :command_category: Inventory"""
        for idx, i in enumerate(c.inventory):
            if i['name'] == item and 'on_eat' in Item.get_item_data(i['internal_name']):
                await Item.get_item_data(i['internal_name'])['on_eat'](i, idx, c)
                return
            elif i['name'] == item:
                await c.send_message('game', 'You can\'t eat a @yel@{}@res@.\n', item)
                return
        await c.send_message('game', 'You don\'t have a @yel@{}@res@.\n', item)

    @autocomplete('inventory')
    def autocomplete_inventory(self, c: 'Character', *inputs: str):
        return [
            f'"{i["name"]}"' if " " in i['name'] else i['name']
            for i in c.inventory
        ] + ['all']
