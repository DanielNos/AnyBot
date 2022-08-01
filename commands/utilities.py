import sys, random
from nextcord.ext import commands
from nextcord import slash_command, Interaction, Embed

sys.path.append("../NosBot")
import logger as log
import dataManager

TEST_GUILDS = []
logger = None


class Utilities(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")

    
    @commands.Cog.listener()
    async def on_ready(self):
        global TEST_GUILDS
        TEST_GUILDS = dataManager.load_test_guilds()


    @slash_command(guild_ids=TEST_GUILDS, description="Chooses between multiple choices.", force_global=True)
    async def choose(self, interaction: Interaction, choices: str):
        logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: choose " + choices + ".")

        embed: Embed = Embed(title="Picked: __" + random.choice(choices.split(" ")) + "__", color=0xFBCE9D)
        embed.add_field(name="Choices:", value=choices, inline=True)
        
        await interaction.response.send_message(embed=embed)


def load(client: commands.Bot):
    client.add_cog(Utilities(client))