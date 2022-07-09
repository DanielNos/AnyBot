import sys
from nextcord.ext import commands
from nextcord import Interaction, slash_command, Embed
sys.path.append("../NosBot")
import dataManager
import logger as log

TEST_GUILDS = []
HELP: Embed = None
logger = None

class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")

    @commands.Cog.listener()
    async def on_ready(self):
        global HELP, TEST_GUILDS

        TEST_GUILDS = dataManager.load_test_guilds()
        HELP = await self.create_help_embed(*dataManager.load_help())
    

    @slash_command(guild_ids=TEST_GUILDS, description="Show all commands and their actions.")
    async def help(self, interaction: Interaction):
        await interaction.response.send_message(embed=HELP)
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: help.")


    async def create_help_embed(self, commands, actions) -> Embed:
        embed: Embed = Embed(title="NosBot Commands", color=0xFBCE9D)

        embed.add_field(name="Command", value=commands, inline=True)
        embed.add_field(name="Action", value=actions, inline=True)

        return embed


def load(client: commands.Bot):
    client.add_cog(Help(client))