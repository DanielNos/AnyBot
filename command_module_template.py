import sys, nextcord
from nextcord.ext import commands
from nextcord import Interaction, slash_command

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import complete_name

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

class Template(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="", force_global=PRODUCTION)
    async def command(self, interaction: Interaction):
        self.logger.log_info(complete_name(interaction.user) + " has called command: ")

        await interaction.response.send_message("")


def load(client: commands.Bot):
    client.add_cog(Template(client))