import os, sys
sys.path.append(os.path.dirname(__file__))

from logging import Logger, getLogger
from nextcord.ext.commands import Cog, Bot
from nextcord import Interaction, slash_command
from config import DEBUG
from mastemind_view import Controls
from mastermind_board import create_board


class Mastermind(Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.logger: Logger = getLogger("bot")
    

    @slash_command(guild_ids=DEBUG["test_guilds"], description="Start a game of mastermind.")
    async def mastermind(self, interaction: Interaction):
        self.logger.info(f"{interaction.user.name} has started a game.")

        await interaction.response.send_message(embed=create_board(), view=Controls(), ephemeral=True)


def load(client: Bot):
    client.add_cog(Mastermind(client))