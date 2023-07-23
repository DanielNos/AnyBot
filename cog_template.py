from logging import Logger, getLogger
from nextcord.ext.commands import Cog, Bot
from nextcord import Interaction, slash_command
from config import *


class NAME(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = getLogger("bot")


def load(client):
    client.add_cog(NAME(client))