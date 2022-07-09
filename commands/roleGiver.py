import nextcord, sys
from nextcord.ext import commands
from nextcord import Message, Interaction, RawMessageDeleteEvent, Role, slash_command, Guild
sys.path.append("../NosBot")
import emoji, dataManager
import logger as log

TEST_GUILDS = []
logger = None

blueprints = {}
role_givers = {}

class RoleGiverObject():
    def __init__(self, message_id: int, role_ids = []):
        self.message_id = message_id
        self.role_ids = role_ids
    
    def to_json(self):
        return {
            "message_id": self.message_id,
            "role_ids": self.role_ids
        }
    
    def __str__(self):
        return "RoleGiver{message_id=" + str(self.message_id) + ", role_ids=" + str(self.role_ids) + "}"


class RoleGiver(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")
    

    @commands.Cog.listener()
    async def on_ready(self):
        global role_givers, TEST_GUILDS
        role_givers = dataManager.load_role_givers()
        TEST_GUILDS = dataManager.load_test_guilds()


    @slash_command(guild_ids=TEST_GUILDS, description="Create a new role giver.")
    async def new_rg(self, interaction: Interaction):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: new_rg.")
        # Remove blueprint if message was deleted
        await self.get_bp_message(interaction)
        
        # Create a new role giver if one doesn't already exist
        if not interaction.user.id in (blueprints.keys()):
            message: Message = await interaction.channel.send("Use /add_role [role name] [*description] to add roles.")
            blueprints[interaction.user.id] = RoleGiverObject(message.id)
            await interaction.response.send_message("✅ Successfully created role giver.", ephemeral=True)
        else:
            await interaction.response.send_message("🚫 FAILED. You already have an unfinished role giver! Complete it or delete it using /del_rg.", ephemeral=True)


    @slash_command(guild_ids=TEST_GUILDS, description="Delete currently edited role giver.")
    async def del_rg(self, interaction: Interaction):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: del_rg.")
        # Check if it was already deleted
        message: Message = await self.get_bp_message(interaction)
        if message == None:
            await interaction.response.send_message("🚫 FAILED. The role giver message was deleted! You can create new one using /new_rg.", ephemeral=True)
            return
        
        # Delete a role giver if it does exist
        if not interaction.user.id in blueprints.keys():
            await interaction.response.send_message("🚫 FAILED. You don't have an unfinished role giver! You can create one by using /new_rg.", ephemeral=True)
        else:
            message: Message = await interaction.channel.fetch_message(blueprints.pop(interaction.user.id).message_id)
            await message.delete()
            await interaction.response.send_message("✅ Successfully deleted role giver.", ephemeral=True)
    

    @slash_command(guild_ids=TEST_GUILDS, description="Lock a role giver and make it functional for users.")
    async def lock_rg(self, interaction: Interaction):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: lock_rg.")
        # Cancel if message was deleted
        message: Message = await self.get_bp_message(interaction)
        if message == None:
            await interaction.response.send_message("🚫 FAILED. The role giver message was deleted! You can create new one using /new_rg.", ephemeral=True)
            return

        # Cancel if no role giver exists
        if not interaction.user.id in blueprints.keys():
            await interaction.response.send_message("🚫 FAILED. You don't have an unfinished role giver! You can create one by using /new_rg.", ephemeral=True)
            return
        
        rg: RoleGiverObject = blueprints[interaction.user.id]
        # Cancel if role giver doesn't have any roles
        if len(rg.role_ids) < 1:
            await interaction.response.send_message("🚫 FAILED. Role giver doesn't have any roles! You can add roles to it using /add_rg_role [role] [*description].", ephemeral=True)
            return
        
        # Remove guide text from role giver message
        await message.edit(content="_Click on a number to receive a role!_" + message.content[message.content.find("\n"):])

        # Move role giver from blueprints dictionary to role_givers dictionary
        role_givers[rg.message_id] = blueprints.pop(interaction.user.id)
        dataManager.save_role_givers(role_givers)

        await interaction.response.send_message("✅ Successfully locked role giver. It can now give roles to users.", ephemeral=True)


    @slash_command(guild_ids=TEST_GUILDS, description="Add role to role giver.")
    async def add_rg_role(self, interaction: Interaction, role: Role, description: str = ""):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: add_rg_role " + role.name + ".")
        # Cancel if message was deleted
        message: Message = await self.get_bp_message(interaction)
        if message == None:
            await interaction.response.send_message("🚫 FAILED. The role giver message was deleted! You can create new one using /new_rg.", ephemeral=True)
            return

        # Cancel if no role giver exists
        if not interaction.user.id in blueprints.keys() or message == None:
            await interaction.response.send_message("🚫 FAILED. You don't have an unfinished role giver! You can create one by using /new_rg.", ephemeral=True)
            return
        
        # Cancel if role doesn't exist or is invalid
        if interaction.guild.get_role(role.id) == None or role.name == "@everyone":
            await interaction.response.send_message("🚫 FAILED. Provided role isn't valid.", ephemeral=True)
            return

        rg: RoleGiverObject = blueprints[interaction.user.id]
        # Cancel if role giver is full
        if len(rg.role_ids) >= 9:
            await interaction.response.send_message("🚫 FAILED. Role giver cant't contain any more roles! Complete it using /lock_rg then create a new role giver using /new_rg for remaining roles.", ephemeral=True)
            return
        
        # Add role to role giver message
        rg.role_ids.append(role.id)
        reaction_emoji = emoji.NUMBERS[len(rg.role_ids)]   

        await message.edit(content=message.content + "\n" + reaction_emoji + " " + str(role.mention) + " " + description)
        await message.add_reaction(reaction_emoji)

        await interaction.response.send_message("✅ Successfully added role to role giver.", ephemeral=True)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: nextcord.RawReactionActionEvent):
        # Cancel if there are no role givers
        if len(role_givers) == 0:
            return
        
        # Cancel if message isn't a role giver
        if (not event.message_id in role_givers.keys()):
            return
        
        role_ids = role_givers[event.message_id].role_ids

        # Remove reaction if it isn't a valid role number
        if not event.emoji.name in list(emoji.NUMBERS.values())[1:len(role_ids)+1]:
            message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)
            for reaction in message.reactions:
                if str(reaction.emoji) == str(event.emoji.name):
                    await message.remove_reaction(emoji=reaction, member=event.member)
                    return
            return

        # Give member the role
        guild: nextcord.Guild = await self.client.fetch_guild(event.guild_id)
        role: Role = guild.get_role(role_ids[int(str(event.emoji.name)[0])-1])
        logger.log_info(event.member.name + "#" + str(event.member.discriminator) + " has received role @" + role.name + " from role giver " + str(event.message_id) + ".")
        await event.member.add_roles(role)
    

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
        logger.log_info(event.member.name + "#" + str(event.member.discriminator) + " has received role @" + role.name + " from role giver " + str(event.message_id) + ".")
        await member.remove_roles(role)

    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in list(role_givers.keys()):
            logger.log_info("Role giver " + str(event.message_id) + " message was deleted. Removing role giver.")
            role_givers.pop(event.message_id)
            dataManager.save_role_givers(role_givers)

    
    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, event: nextcord.RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in list(role_givers.keys()):
                logger.log_info("Role giver " + str(id) + " message was deleted. Removing role giver.")
                role_givers.pop(id)
                dataManager.save_role_givers(role_givers)
                return


    async def get_bp_message(self, interaction: Interaction) -> Message:
        if not interaction.user.id in list(blueprints.keys()):
            return None
        
        try:
            return await interaction.channel.fetch_message(blueprints[interaction.user.id].message_id)
        except:
            blueprints.pop(interaction.user.id)
            return None


def load(client: commands.Bot):
    client.add_cog(RoleGiver(client))