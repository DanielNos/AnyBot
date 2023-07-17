import logging
from logging import Logger
from nextcord.ext.commands import Cog, Bot
from nextcord import Message, Interaction, Embed, slash_command
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
        if message.author.id == self.client.user.id:
            return

        text = ""

        # Log user type
        if message.author.bot:
            text += "[bot]"

        text += f"[{message.author.name}]"

        # Log attachments
        if len(message.attachments) > 0:
            text += f" [attachments:"
            
            for attachment in message.attachments:
                text += f" ({attachment.filename} : {attachment.url})"

            text += "]"

        text += f" {message.content}"

        self.chat.info(text)


    @slash_command(name="nosbot", description=f"Shows information about {config.BOT['name']}.", guild_ids=config.DEBUG["test_guilds"])
    async def nosbot(self, interaction: Interaction):

        embed: Embed = Embed(title=f"{config.BOT['name']}", color=config.BOT["color"])
        embed.set_thumbnail(url=config.BOT["icon"])
        
        embed.add_field(name="Commands", value=len(self.client.commands))
        embed.add_field(name="Guilds", value=len(self.client.guilds))
        embed.add_field(name="Latency", value=f"{round(self.client.latency * 1000)} ms")
        embed.add_field(name="Author", value=f"[{config.AUTHOR['name']}]({config.AUTHOR['url']})", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


def load(client):
    client.add_cog(Core(client))