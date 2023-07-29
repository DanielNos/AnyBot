import os
from datetime import datetime
from logging import Logger, getLogger
from nextcord.ext.commands import Cog, Bot, Context, command
from nextcord.ext.tasks import loop
from nextcord import Member, Guild
from config import *


LOGGED_USERS = [(533327218403835905, "danda174")]
LOGGED_GUILDS = [793074039996416012]


class StatusLogger(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = getLogger("bot")
    

    @Cog.listener()
    async def on_ready(self):
        self.log_task.start()

    
    @loop(minutes=10)
    async def log_task(self):
        await self.log_statuses()

    
    @command()
    async def log(self, ctx: Context):
        await self.log_statuses()


    async def log_statuses(self):
        self.logger.info("Logging statuses...")

        # Check if folder and files exist
        if not os.path.exists("./modules_data/status_logger/"):
            os.mkdir("./modules_data/status_logger")

        for user_tuple in LOGGED_USERS:
            if not os.path.exists(f"./modules_data/status_logger/{user_tuple[1]}"):
                file = open(f"./modules_data/status_logger/{user_tuple[1]}", "x")
                file.write("")
                file.close()
        
        for guild_id in LOGGED_GUILDS:
            # Fetch guild
            try:
                guild: Guild = await self.client.fetch_guild(guild_id)
            except:
                self.logger.error(f"Failed to fetch guild {guild_id}.")
                continue
            
            for user_tuple in LOGGED_USERS:
                # Fetch user
                try:
                    member: Member = await guild.fetch_member(user_tuple[0])
                except:
                    self.logger.error(f"Failed to fetch user {user_tuple[1]}.")

                file = open(f"./modules_data/status_logger/{user_tuple[1]}", "a")
                file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} {member.status}\n")
                file.close()


def load(client):
    client.add_cog(StatusLogger(client))