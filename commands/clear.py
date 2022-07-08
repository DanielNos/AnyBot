import sys
from nextcord.ext import commands
from nextcord import Interaction, slash_command
sys.path.append("../NosBot")
import dataManager

TEST_GUILDS = []

class Clear(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        global TEST_GUILDS
        TEST_GUILDS = dataManager.load_test_guilds()
    

    @slash_command(guild_ids=TEST_GUILDS, description="Deletes up to 100 messages from current channel.")
    async def clear(self, interaction: Interaction, amount: int):
        if amount > 100: amount = 100
        if amount < 0: amount = 0

        messages = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"✅ Successfully removed {len(messages)} message" + ((len(messages)!=1)*"s") + ".", ephemeral=True)


def load(client: commands.Bot):
    client.add_cog(Clear(client))