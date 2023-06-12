import logging
from logging import Logger
from discord.ext.commands import Cog, Bot
from discord.app_commands import command
from discord import Message, Interaction, Embed
import config


class Core(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")
        self.chat: Logger = logging.getLogger("chat")
    
    
    @Cog.listener()
    async def on_ready(self):
        self.logger.info(f"Logged in as {self.client.user} ({self.client.user.id}).")


    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.author.bot:
            self.chat.info(f"[{message.author.name}] {message.content}")


    @command(name="info", description=f"Shows information about {config.BOT['name']}.")
    async def info(self, interaction: Interaction):

        embed: Embed = Embed(title=f"{config.BOT['name']}", color=config.BOT["color"])
        embed.set_thumbnail(url=config.BOT["icon"])
        
        embed.add_field(name="Commands", value=len(self.client.all_commands))
        embed.add_field(name="Guilds", value=len(self.client.guilds))
        embed.add_field(name="Latency", value=f"{round(self.client.latency * 1000)} ms")
        embed.add_field(name="Author", value=f"[{config.AUTHOR['name']}]({config.AUTHOR['url']})", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client):
    await client.add_cog(Core(client))