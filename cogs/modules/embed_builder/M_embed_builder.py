import os, sys
sys.path.append(os.path.dirname(__file__))

import logging
from logging import Logger
from nextcord.ext.commands import Cog, Bot
from nextcord import Embed, Interaction, slash_command
import config
from embed_builder_view import EmbedBuilderEditor


class EmbedBuilder(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")


    @slash_command(name="create_embed", description="Opens new embed builder.")
    async def create_embed(self, interaction: Interaction):

        embed: Embed = Embed(description="description")
        await interaction.response.send_message(embed=embed, view=EmbedBuilderEditor(self.logger, embed, interaction.user.id))



def load(client):
    client.add_cog(EmbedBuilder(client))