import logging
from logging import Logger
from discord.ext.commands import Cog, Bot
from discord import Object
import config


class CommandsSyncer(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")
        self.chat: Logger = logging.getLogger("chat")
    
    
    @Cog.listener()
    async def on_ready(self):
        self.logger.info("Synchronizing commands with Discord.")
        synced = 0

        try:
            if config.DEBUG["enabled"]:
                self.client.tree.copy_global_to(guild=Object(id=config.DEBUG["test_guild"]))
                synced = len(await self.client.tree.sync(guild=Object(id=config.DEBUG["test_guild"])))
            else:
                synced = len(await self.client.tree.sync())

        except Exception as exception:
            self.logger.critical(f"Failed to synchronize commands: {exception}")
            exit(1)

        self.logger.info(f"Synchronized {synced} commands.")
    

async def setup(client):
    await client.add_cog(CommandsSyncer(client))