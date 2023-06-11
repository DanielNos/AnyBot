import logging
from logging import Logger
from discord.app_commands import command
from discord.ext.commands import Cog, Bot
import config


class NAME(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")


async def setup(client):
    await client.add_cog(NAME(client))