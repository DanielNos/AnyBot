import logging
from logging import Logger
from discord import Interaction
from discord.app_commands import command
from discord.ext.commands import Cog, Bot


class Utilities(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")


    @command(name="clear", description="Removes specified amount of messages. By default 5.")
    async def clear(self, interaction: Interaction, amount: int = 5):
        
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Failed. Invalid amount.", ephemeral=True)
            return
        
        await interaction.channel.purge(limit=amount)


async def setup(client):
    await client.add_cog(Utilities(client))