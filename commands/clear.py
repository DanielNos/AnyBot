from nextcord.ext import commands
from nextcord import Interaction, slash_command, Embed

TEST_GUILD = 794290505273966604

class Clear(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    @slash_command(guild_ids=[TEST_GUILD], description="Deletes up to 100 messages from current channel.")
    async def clear(self, interaction: Interaction, amount: int = 5):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"✅ Successfully removed {amount} messages.", ephemeral=True)


def load(client: commands.Bot):
    client.add_cog(Clear(client))