import logging
from logging import Logger
from nextcord import Interaction, slash_command
from nextcord.ext.commands import Cog, Bot
import config


class Utilities(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")


    @slash_command(name="clear", description="Removes specified amount of messages. By default 5.", guild_ids=config.DEBUG["test_guilds"])
    async def clear(self, interaction: Interaction, amount: int = 5):
        
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Failed. Invalid amount.", ephemeral=True)
            return
        
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"✅ Successfully removed {len(deleted)} messages.", ephemeral=True)


def load(client):
    client.add_cog(Utilities(client))