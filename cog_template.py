import logging
from logging import Logger
from nextcord.ext.commands import Cog, Bot
from nextcord import Interaction, slash_command
import config


class NAME(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")


def load(client):
    client.add_cog(NAME(client))