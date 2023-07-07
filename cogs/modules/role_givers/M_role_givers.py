import os, sys
sys.path.append(os.path.dirname(__file__))

import logging
from logging import Logger
from typing import Dict, List
from nextcord.ext.commands import Cog, Bot
from nextcord import Interaction, PartialInteractionMessage, Role, RawReactionActionEvent, Guild, TextChannel, Message, slash_command
from role_givers_views import FullBlueprintView, RoleGiverDelete
from role_givers_limited_view import LimitedBlueprintView
from role_giver import RoleGiver, RoleGiverBlueprint
from emoji import is_emoji
import config


NUMBERS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣", "🔟"]


class RoleGivers(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")

        self.role_givers: Dict[int, RoleGiver] = {}
        self.role_giver_blueprints: Dict[int, RoleGiverBlueprint] = {}
    

    def add_role_giver(self, message_id: int, role_giver):
        self.role_givers[message_id] = role_giver

    
    @Cog.listener()
    async def on_ready(self):

        # LOAD ROLE GIVERS
        return
        # Check if folder exists
        if not os.path.exists("./modules_data/role_givers/"):
            os.mkdir("./modules_data/role_givers/")
        
        # Check if file exists
        if not os.path.exists("./modules_data/role_givers/role_givers"):
            file = open("./modules_data/role_givers/role_givers", "w")
            file.write("{}")
            file.close()
            return
        
        # Read lines
        file = open("./modules_data/role_givers/role_givers", "r")
        lines = file.readlines()
        file.close()

        to_remove = []

        # Process lines
        index = 0
        for line in lines:
            # Split line to parts
            parts = line[:-1].split(";")

            # Collect role giver info
            guild_id, channel_id, message_id = parts[0].split(":")

            del parts[0]

            # Fetch guild
            try:
                guild: Guild = await self.client.fetch_guild(int(guild_id), with_counts=False)
            except:
                self.logger.error(f"Role givers module failed to fetch guild with id: {guild_id}")
                continue

            # Bot was removed from guild
            if guild not in self.client.guilds:
                to_remove.append(index)
                continue
            
            # Fetch channel
            try:
                channel: TextChannel = await guild.fetch_channel(int(channel_id))
            except:
                continue

            # Collect roles
            

            index += 1
                


    @slash_command(name="role_giver", guild_ids=config.DEBUG["test_guilds"])
    async def role_giver(self, interaction: Interaction):
        pass


    @role_giver.subcommand(name="create", description="Creates a new role giver blueprint.")
    async def create(self, interaction: Interaction, text: str = None):
        
        # No active blueprint
        if interaction.user.id in self.role_giver_blueprints:
            
            # Message still exists
            try:
                await self.role_giver_blueprints[interaction.user.id].message.edit(delete_after=None)
                await interaction.response.send_message(content="❌ You currently have one role giver blueprint open.\nWould you like to delete it and make a new one?", view=RoleGiverDelete(self.role_giver_blueprints, interaction.user.id))
                return
            # Message was removed
            except:
                self.role_giver_blueprints.pop(interaction.user.id)
        
        if text is None:
            text = "Click on a emoji to receive a role!"

        # Create blueprint and message
        blueprint = RoleGiverBlueprint()
        message: PartialInteractionMessage = await interaction.response.send_message(text, view=LimitedBlueprintView(interaction.user.id))

        # Save message to blueprint and add it do dict
        blueprint.message = await message.fetch()
        self.role_giver_blueprints[interaction.user.id] = blueprint


    @role_giver.subcommand(name="add_role", description="Adds role to currently edited role giver.")
    async def add_role(self, interaction: Interaction, role: Role, text: str = None, emoji: str = None):
        
        # No active blueprint
        if not interaction.user.id in self.role_giver_blueprints:
            await interaction.response.send_message("❌ You don't have any role giver blueprints. Use `role_giver create` to make one.", ephemeral=True)
            return
        
        blueprint: RoleGiverBlueprint = self.role_giver_blueprints[interaction.user.id]
        
        # Too many roles
        if len(blueprint.roles) >= 10:
            await interaction.response.send_message("❌ Can't add more than 10 roles to one role giver.", ephemeral=True)
            return
        
        # Collect bots roles
        for bot in interaction.guild.bots:
            if bot.id == self.client.user.id:
                bot_roles: List[Role] = bot.roles
                break
        
        # Check if he can assign this role
        if role.is_bot_managed():
            await interaction.response.send_message("❌ This role is bot managed. It can't be assigned to users.", ephemeral=True)
            return

        # Check bot has permission to assign this role
        lower = False
        for r in bot_roles:
            if role < r:
                lower = True
                break
                
        # It can't assign it
        if not lower:
            await interaction.response.send_message(f"❌ This role is above or equal to the highest {config.BOT['name']}s role. {config.BOT['name']} can assign only roles lower than his.", ephemeral=True)
            return

        # Emoji is provided
        if emoji is not None:
            # Invalid emoji
            if not is_emoji(emoji):
                await interaction.response.send_message("❌ Invalid emoji.", ephemeral=True)
                return
            
            # Duplicate emoji
            for r in blueprint.roles:
                if r[2] == emoji:
                    await interaction.response.send_message("❌ Emoji is already used.", ephemeral=True)
                    return
                
        # Emoji isn't provided
        else:
            emoji = NUMBERS[len(blueprint.roles)]
        
        await interaction.response.defer()
        
        # Add role
        blueprint.add_role(role, text, emoji)

        # Create new view
        role_giver_view = FullBlueprintView(blueprint, self.role_givers, interaction.user.id)

        # Update messsage
        new_content = f"{blueprint.message.content}\n{emoji} {role.mention} {'' if text is None else text}"
        blueprint.message.content = new_content

        # Edit message
        await blueprint.message.edit(content=new_content, view=role_giver_view)
        await interaction.followup.send(f"✅ Added role {role}.", delete_after=3)


    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        
        # Reaction is by bot
        if payload.user_id == self.client.user.id:
            return

        # Message isn't a role giver
        if payload.message_id not in self.role_givers:
            return
        
        role_giver = self.role_givers[payload.message_id]
        
        # Collect message
        channel = await self.client.fetch_channel(payload.channel_id)
        message: Message = await channel.fetch_message(payload.message_id)

        # Emoji isn't valid reaction
        if payload.emoji.name not in role_giver.roles:
            await message.remove_reaction(payload.emoji, payload.member)
            return
        
        await payload.member.add_roles(role_giver.roles[payload.emoji.name])


    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        
        # Reaction is by bot
        if payload.user_id == self.client.user.id:
            return

        # Message isn't a role giver
        if payload.message_id not in self.role_givers:
            return
        
        role_giver = self.role_givers[payload.message_id]

        # Emoji isn't valid reaction
        if payload.emoji.name not in role_giver.roles:
            return
        
        await payload.member.remove_roles(role_giver.roles[payload.emoji.name])


def load(client):
    client.add_cog(RoleGivers(client))