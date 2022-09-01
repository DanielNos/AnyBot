import nextcord, sys
from nextcord.ext import commands
from nextcord.ui import View, Button, Modal, TextInput
from nextcord import slash_command, ButtonStyle, Message, Interaction, RawMessageDeleteEvent, Role, Guild, PartialInteractionMessage

sys.path.append("../NosBot")
import dataManager, access, formatting
import logger as log
from dataClasses import RoleGiver

PRODUCTION = dataManager.is_production()
TEST_GUILDS = dataManager.load_test_guilds()

blueprints = {}
role_givers = {}


class AddRole(Modal):
    def __init__(self, logger: log.Logger):
        super().__init__(title="Add Role")
        self.logger = logger

        # Add inputs
        self.role_input = TextInput(label="Role Name:", min_length=1, max_length=50, required=True)
        self.add_item(self.role_input)

        self.description = TextInput(label="Description:", min_length=0, max_length=50, required=False, placeholder="This can be empty.")
        self.add_item(self.description)
    

    async def callback(self, interaction: Interaction):
        for role in interaction.guild.roles:
            if role.name.lower() == self.role_input.value.lower():
                await self.add_rg_role(interaction, role)
                return
        await interaction.response.defer()
    

    async def add_rg_role(self, interaction: Interaction, role: Role):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: add_rg_role " + role.name + ".")
        
        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Manage Role Givers"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission manage role givers.", ephemeral=True)
            return
        
        # Cancel if message was deleted
        message: Message = await get_bp_message(interaction)
        if message == None:
            await interaction.response.send_message("🚫 FAILED. The role giver message was deleted! You can create new one using /new_rg.", ephemeral=True)
            return

        # Cancel if no role giver exists
        if not interaction.user.id in blueprints.keys() or message == None:
            await interaction.response.send_message("🚫 FAILED. You don't have an unfinished role giver! You can create one by using /new_rg.", ephemeral=True)
            return

        rg: RoleGiver = blueprints[interaction.user.id]
        # Cancel if role giver is full
        if len(rg.role_ids) >= 9:
            await interaction.response.send_message("🚫 FAILED. Role giver cant't contain any more roles! Complete it using /lock_rg then create a new role giver using /new_rg for remaining roles.", ephemeral=True)
            return
        
        # Add role to role giver message
        rg.role_ids.append(role.id)
        reaction_emoji = formatting.NUMBERS[len(rg.role_ids)]

        await message.edit(content=message.content + "\n" + reaction_emoji + " " + role.mention + " " + self.description.value, view=RoleGiverDesigner(self.logger, True))
        await message.add_reaction(reaction_emoji)


class RoleGiverDesigner(View):
    def __init__(self, logger: log.Logger, enable_complete = False):
        super().__init__()
        self.logger = logger

        # Add controls
        button: Button = Button(style=ButtonStyle.blurple, label="Add Role")
        button.callback = self.add_rg_role
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.red, label="Delete")
        button.callback = self.del_rg
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.green, label="Complete", disabled=(not enable_complete))
        button.callback = self.lock_rg
        self.add_item(button)
    

    async def add_rg_role(self, interaction: Interaction):
        await interaction.response.send_modal(AddRole(self.logger))
    

    async def del_rg(self, interaction: Interaction):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: del_rg.")

        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Manage Role Givers"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission manage role givers.", ephemeral=True)
            return

        # Check if it was already deleted
        message: Message = await get_bp_message(interaction)
        if message == None:
            await interaction.response.send_message("🚫 FAILED. The role giver message was deleted! You can create new one using /new_rg.", ephemeral=True)
            return
        
        # Delete a role giver if it does exist
        if not interaction.user.id in blueprints.keys():
            await interaction.response.send_message("🚫 FAILED. You don't have an unfinished role giver! You can create one by using /new_rg.", ephemeral=True)
        else:
            message: Message = await interaction.channel.fetch_message(blueprints.pop(interaction.user.id).message_id)
            await message.delete()
    

    async def lock_rg(self, interaction: Interaction):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: lock_rg.")

        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Manage Role Givers"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission manage role givers.", ephemeral=True)
            return

        # Cancel if message was deleted
        message: Message = await get_bp_message(interaction)
        if message == None:
            await interaction.response.send_message("🚫 FAILED. The role giver message was deleted! You can create new one using /new_rg.", ephemeral=True)
            return

        # Cancel if no role giver exists
        if not interaction.user.id in blueprints.keys():
            await interaction.response.send_message("🚫 FAILED. You don't have an unfinished role giver! You can create one by using /new_rg.", ephemeral=True)
            return
        
        rg: RoleGiver = blueprints[interaction.user.id]
        # Cancel if role giver doesn't have any roles
        if len(rg.role_ids) < 1:
            await interaction.response.send_message("🚫 FAILED. Role giver doesn't have any roles! You can add roles to it using /add_rg_role [role] [*description].", ephemeral=True)
            return
        
        # Remove guide text from role giver message
        await message.edit(content="_Click on a number to receive a role!_" + message.content[message.content.find("\n"):])

        # Move role giver from blueprints dictionary to role_givers dictionary
        role_givers[rg.message_id] = blueprints.pop(interaction.user.id)
        dataManager.save_role_givers(role_givers)

        # Remove controls
        self.children.clear()
        await interaction.response.edit_message(view=self)


class RoleGivers(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @commands.Cog.listener()
    async def on_ready(self):
        global role_givers
        role_givers = dataManager.load_role_givers()


    @slash_command(guild_ids=TEST_GUILDS, description="Create a new role giver.", force_global=PRODUCTION)
    async def role_giver(self, interaction: Interaction):
        return
    

    @role_giver.subcommand(description="Create a new role giver.")
    async def create(self, interaction: Interaction):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: role_giver create.")

        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Manage Role Givers"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission manage role givers.", ephemeral=True)
            return

        # Remove blueprint if message was deleted
        await get_bp_message(interaction)
        
        # Create a new role giver if one doesn't already exist
        if not interaction.user.id in (blueprints.keys()):
            response: PartialInteractionMessage = await interaction.response.send_message(content="Add roles to this role giver and then complete it using the buttons below.", view=RoleGiverDesigner(self.logger), ephemeral=True)
            
            message: Message = await response.fetch()
            blueprints[interaction.user.id] = RoleGiver(message.id)
        else:
            await interaction.response.send_message("🚫 FAILED. You already have an unfinished role giver! Complete it or delete it using the controls under it.", ephemeral=True)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: nextcord.RawReactionActionEvent):
        # Cancel if there are no role givers
        if len(role_givers) == 0:
            return
        
        # Cancel if message isn't a role giver
        if not event.message_id in role_givers.keys():
            return
        
        role_ids = role_givers[event.message_id].role_ids

        # Remove reaction if it isn't a valid role number
        if not event.emoji.name in list(formatting.NUMBERS.values())[1:len(role_ids)+1]:
            message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)
            for reaction in message.reactions:
                if str(reaction.emoji) == str(event.emoji.name):
                    await message.remove_reaction(emoji=reaction, member=event.member)
                    return
            return

        # Give member the role
        guild: nextcord.Guild = await self.client.fetch_guild(event.guild_id)
        role: Role = guild.get_role(role_ids[int(str(event.emoji.name)[0])-1])
        
        await event.member.add_roles(role)

        self.logger.log_info(event.member.name + "#" + event.member.discriminator + " has received role @" + str(role) + " from role giver " + str(event.message_id) + ".")
    

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, event: nextcord.RawReactionActionEvent):
        # Cancel if there are no role givers
        if len(role_givers) == 0:
            return

        # Cancel if message isn't a role giver
        if not event.message_id in role_givers.keys():
            return
        
        role_ids = role_givers[event.message_id].role_ids
        role = role_ids[int(str(event.emoji.name)[0])-1]
        
        # Give member the role
        guild: Guild = await self.client.fetch_guild(event.guild_id)
        role: Role = guild.get_role(role_ids[int(str(event.emoji.name)[0])-1])
        member = await self.client.get_guild(event.guild_id).fetch_member(event.user_id)
        
        await member.remove_roles(role)

        self.logger.log_info(member.name + "#" + member.discriminator + " has received role @" + str(role) + " from role giver " + str(event.message_id) + ".")

    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in role_givers.keys():
            self.logger.log_info("Role giver " + str(event.message_id) + " message was deleted. Removing role giver.")
            role_givers.pop(event.message_id)
            dataManager.save_role_givers(role_givers)

    
    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, event: nextcord.RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in role_givers.keys():
                self.logger.log_info("Role giver " + str(id) + " message was deleted. Removing role giver.")
                role_givers.pop(id)
                dataManager.save_role_givers(role_givers)


async def get_bp_message(interaction: Interaction) -> Message:
        if not interaction.user.id in list(blueprints.keys()):
            return None
        
        try:
            return await interaction.channel.fetch_message(blueprints[interaction.user.id].message_id)
        except:
            blueprints.pop(interaction.user.id)
            return None


def load(client: commands.Bot):
    client.add_cog(RoleGivers(client))