import os, sys
sys.path.append(os.path.dirname(__file__))

import logging
from logging import Logger
from nextcord.ext.commands import Cog, Bot
from nextcord import Embed, Interaction, slash_command
from embed_builder_view import EmbedBuilderEditor
from formatting import get_place


class EmbedBuilder(Cog):
    def __init__(self, client: Bot):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")


    @slash_command(description="Opens new embed builder.")
    async def create_embed(self, interaction: Interaction):

        embed: Embed = Embed(description="description")
        await interaction.response.send_message(embed=embed, view=EmbedBuilderEditor(self.logger, embed, interaction.user.id))
        
        self.logger.info(f"{interaction.user.name} has created new embed builder in {get_place(interaction)}.")


def load(client):
    client.add_cog(EmbedBuilder(client))
