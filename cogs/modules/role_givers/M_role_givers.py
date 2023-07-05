import os, sys
sys.path.append(os.path.dirname(__file__))

import logging
from logging import Logger
from typing import Dict
from nextcord.ext.commands import Cog, Bot
from nextcord.guild import GuildChannel
from nextcord import Interaction, PartialInteractionMessage, Role, Member, RawReactionActionEvent, Reaction, Message, slash_command
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
            text = "Click on a number to receive a role!"

        # Create blueprint and message
        blueprint = RoleGiverBlueprint()
        message: PartialInteractionMessage = await interaction.response.send_message(text, view=LimitedBlueprintView())

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

        # Emoji is provided
        if emoji is not None:
            # Invalid emoji
            if not is_emoji(emoji):
                await interaction.response.send_message("❌ Invalid emoji.", ephemeral=True)
                return
            
            # Duplicate emoji
            for role in blueprint.roles:
                if role[2] == emoji:
                    await interaction.response.send_message("❌ Emoji is already used.", ephemeral=True)
                    return
                
        # Emoji isn't provided
        else:
            emoji = NUMBERS[len(blueprint.roles)]
        
        await interaction.response.defer()
        
        # Add role
        blueprint.add_role(role, text, emoji)

        # Create new view
        role_giver_view = FullBlueprintView(blueprint, self.role_givers)

        # Update messsage
        await blueprint.message.edit(content=f"{blueprint.message.content}\n{emoji} {role.mention} {'' if text is None else text}", view=role_giver_view)
        await interaction.followup.send(f"✅ Added role {role}.", delete_after=3)

    
    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member):
        print(type(user))
        # Message isn't role giver 
        if reaction.message.id not in self.role_givers or user.bot:
            return
        
        role_giver = self.role_givers[reaction.message.id]
        
        # Emoji isn't valid reaction
        if reaction.emoji not in role_giver.roles:
            await reaction.remove(user)
            return
        
        await user.add_roles(role_giver.roles[reaction.emoji])


    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        
        # Message isn't role giver 
        if payload.message_id not in self.role_givers:
            return
        
        role_giver = self.role_givers[payload.message_id]
        
        # Collect message
        channel: GuildChannel = await self.client.fetch_channel(payload.channel_id)
        message: Message = channel.fetch_message(payload.message_id)

        # Emoji isn't valid reaction
        if payload.emoji not in role_giver.roles:
            await message.remove_reaction(user)
            return
        
        await user.add_roles(role_giver.roles[reaction.emoji])


def load(client):
    client.add_cog(RoleGivers(client))