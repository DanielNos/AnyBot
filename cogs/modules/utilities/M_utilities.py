import logging
from logging import Logger
from discord import Interaction, Message
from discord.app_commands import command
from discord.ext.commands import Cog, Bot
import config


class Utilities(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")


    @command(name="clear", description="Removes specified amount of messages. By default 5.")
    async def clear(self, interaction: Interaction, amount: int = 5):
        
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Failed. Invalid amount.", ephemeral=True)
            return
        deleted = []
        await interaction.response.send_message(f"✅ Removed {len(deleted)} messages.", ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount, check=lambda message: message.id != interaction.response)
        await interaction.response.edit_message(content="A")


async def setup(client):
    await client.add_cog(Utilities(client))