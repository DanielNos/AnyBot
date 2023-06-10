import logging
from logging import Logger
from discord.ext.commands import Cog, Bot
from discord.app_commands import command
from discord import Message, Interaction, Embed


class Core(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")
        self.chat: Logger = logging.getLogger("chat")
    
    @Cog.listener()
    async def on_ready(self):
        self.logger.info(f"Logged in as {self.client.user}.")

    @Cog.listener()
    async def on_message(self, message: Message):
        self.chat.info(f"[{message.author._user}] {message.content}")

    @command()
    async def info(self, interaction: Interaction):
        await interaction.response.send


async def setup(client):
    await client.add_cog(Core(client))