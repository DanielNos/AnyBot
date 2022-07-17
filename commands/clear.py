import sys
from nextcord.ext import commands
from nextcord import Interaction, slash_command
sys.path.append("../NosBot")
import dataManager
import logger as log

TEST_GUILDS = []
logger = None

class Clear(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")


    @commands.Cog.listener()
    async def on_ready(self):
        global TEST_GUILDS
        TEST_GUILDS = dataManager.load_test_guilds()
    

    @slash_command(guild_ids=TEST_GUILDS, description="Deletes up to 100 messages from current channel.", force_global=True)
    async def clear(self, interaction: Interaction, amount: int):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: clear " + str(amount) +".")
        if amount > 100: amount = 100
        if amount < 0: amount = 0

        messages = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"✅ Successfully removed {len(messages)} message" + ((len(messages)!=1)*"s") + ".", ephemeral=True)


def load(client: commands.Bot):
    client.add_cog(Clear(client))