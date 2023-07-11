import os, json
from logging import Logger, getLogger
from typing import Dict
from nextcord.ui import View, Button, button
from nextcord import ButtonStyle, Interaction, Message
from role_giver_classes import RoleGiverBlueprint, RoleGiver
from role_givers_modals import RemoveRoleModal


def safe_insert(dict: Dict, key1, key2, key3, value):
    if key1 in dict:
        if key2 in dict[key1]:
            dict[key1][key2][key3] = value
        else:
            dict[key1][key2] = {key3: value}
    else:
        dict[key1] = {key2: {key3: value}}


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
    def __init__(self, blueprint: RoleGiverBlueprint, role_givers: Dict[int, RoleGiver], editor_id: int):
        super().__init__(timeout=None)
        self.logger: Logger = getLogger("bot")
        self.blueprint: RoleGiverBlueprint = blueprint
        self.role_givers: Dict[int, RoleGiver] = role_givers
        self.editor_id = editor_id

    
    @button(label="Use /role_giver add_role [role] (text) (emoji)")
    async def add_role(self, button: Button, interaction: Interaction):
        await interaction.response.defer()

    
    @button(label="Remove Role", style=ButtonStyle.blurple)
    async def remove_role(self, button: Button, interaction: Interaction):

        # Allow only creator to edit
        if interaction.user.id != self.editor_id:
            await interaction.response.defer()
            return

        await interaction.response.send_modal(RemoveRoleModal(self.blueprint))

    
    @button(label="Complete", style=ButtonStyle.green)
    async def complete(self, button: Button, interaction: Interaction):
        
        await interaction.response.defer()

        # Allow only creator to edit
        if interaction.user.id != self.editor_id:
            return
        
        # Delete original message
        await interaction.message.delete()

        # Create emoji to role dictionary
        roles = {}
        for role in self.blueprint.roles:
            roles[role[2]] = role[0]

        # Create new message and role giver
        message: Message = await interaction.channel.send(interaction.message.content)
        safe_insert(self.role_givers, interaction.guild_id, interaction.channel_id, message.id, RoleGiver(message, roles))
        
        # SAVE ROLE GIVER
        # Check if folder exists
        if not os.path.exists("./modules_data/role_givers/"):
            os.mkdir("./modules_data/role_givers/")
        
        # Check if file exists
        if not os.path.exists("./modules_data/role_givers/role_givers"):
            file = open("./modules_data/role_givers/role_givers", "w")
            file.write("{}")
            file.close()

        # Read data
        with open("./modules_data/role_givers/role_givers", "r") as file:
            json_obj = json.load(file)
        
        # Flatten roles (nextcord.Message -> message_id: int)
        json_roles = {}
        for role in roles:
            json_roles[role] = roles[role].id

        # Insert data
        safe_insert(json_obj, str(interaction.guild_id), str(interaction.channel_id), str(message.id), json_roles)

        # Save data
        with open("./modules_data/role_givers/role_givers", "w") as file:
            file.write(json.dumps(json_obj, indent=4))
        
        # Add reactions to message
        for role in self.blueprint.roles:
            await message.add_reaction(role[2])
    

    @button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, button: Button, interaction: Interaction):

        # Allow only creator to edit
        if interaction.user.id != self.editor_id:
            await interaction.response.defer()
            return

        await interaction.message.delete()