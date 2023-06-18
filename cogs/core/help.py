import logging
from logging import Logger
from nextcord import slash_command
from nextcord.ext.commands import Cog, Bot
import config


class Help(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")
        

def load(client):
    client.add_cog(Help(client))