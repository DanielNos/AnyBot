import os, sys
sys.path.append(os.path.dirname(__file__))

import logging
from logging import Logger
from nextcord.ext.commands import Cog, Bot
from nextcord import Interaction, slash_command
from cogs.modules.role_givers.role_givers_views import RoleGiverView, RoleGiverDelete
import config


class RoleGivers(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")

        self.role_givers = {}
        self.role_giver_blueprints = {}
    

    def add_role_giver(self, message_id: int, role_giver):
        self.role_givers[message_id] = role_giver


    @slash_command(name="role_giver")
    async def role_giver(self, interaction: Interaction):
        pass


    @role_giver.subcommand(name="create", description="Creates a new role giver blueprint.", guild_ids=config.DEBUG["test_guilds"])
    async def create(self, interaction: Interaction):

        if interaction.user.id in self.role_giver_blueprints:
            await interaction.response.send_message(content="❌ You currently have one role giver blueprint open.\nWould you like to delete it and make a new one?", view=RoleGiverDelete())
            return
        
        await interaction.response.send_message(content="Click on a number to receive a role!", view=RoleGiverView(self.logger, self))


    @role_giver.subcommand(name="add_role", description="Adds role to currently edited role giver.", guild_ids=config.DEBUG["test_guilds"])
    async def add_role(self, interaction: Interaction):

        if not interaction.user.id in self.role_giver_blueprints:
            await interaction.response.send_message("❌ You don't have any role giver blueprints.\nUse `role_giver create` to make one.")
            return
        
        

        await interaction.response.send_message(content="Click on a number to receive a role!", view=RoleGiverView(self.logger, self))



def load(client):
    client.add_cog(RoleGivers(client))