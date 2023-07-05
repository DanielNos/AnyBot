from logging import Logger, getLogger
from typing import Dict
from nextcord.ui import View, Button, button
from nextcord import ButtonStyle, Interaction, Message
from role_giver import RoleGiverBlueprint, RoleGiver
from role_givers_modals import RemoveRoleModal


class RoleGiverDelete(View):
    def __init__(self, blueprints: Dict[int, RoleGiverBlueprint], user_id: int):
        super().__init__(timeout=None)
        self.blueprints: Dict[int, RoleGiverBlueprint] = blueprints
        self.user_id = user_id

    
    @button(label="Yes, delete it", style=ButtonStyle.red)
    async def delete(self, button: Button, interaction: Interaction):
        # Remove blueprint message if it exists
        try:
            message = await self.blueprints[self.user_id].message.channel.fetch_message(self.blueprints[self.user_id].message.id)
            await message.delete()
        except:
            pass

        await interaction.message.delete()


    @button(label="No, keep it", style=ButtonStyle.green)
    async def keep(self, button: Button, interaction: Interaction):
        await interaction.message.delete()


class FullBlueprintView(View):
    def __init__(self, blueprint: RoleGiverBlueprint, role_givers: Dict[int, RoleGiver]):
        super().__init__(timeout=None)
        self.logger: Logger = getLogger("bot")
        self.blueprint: RoleGiverBlueprint = blueprint
        self.role_givers: Dict[int, RoleGiver] = role_givers

    
    @button(label="Use /role_giver add_role [role] (text) (emoji)")
    async def add_role(self, button: Button, interaction: Interaction):
        await interaction.response.defer()

    
    @button(label="Remove Role", style=ButtonStyle.blurple)
    async def remove_role(self, button: Button, interaction: Interaction):

        await interaction.response.send_modal(RemoveRoleModal(self.blueprint))

    
    @button(label="Complete", style=ButtonStyle.green)
    async def complete(self, button: Button, interaction: Interaction):
        
        # Delete original message
        await interaction.message.delete()

        # Create emoji to role dictionary
        roles = {}
        for role in self.blueprint.roles:
            roles[role[2]] = role[0]

        # Create new message and role giver
        message: Message = await interaction.channel.send(interaction.message.content)
        self.role_givers[message.id] = RoleGiver(roles)
        
        # Add reactions to message
        for role in self.blueprint.roles:
            await message.add_reaction(role[2])
    

    @button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, button: Button, interaction: Interaction):

        await interaction.message.delete()