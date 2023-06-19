import logging
from logging import Logger
from nextcord import Interaction, User, Embed, slash_command
from nextcord.ext.commands import Cog, Bot
import config


class Utilities(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")


    @slash_command(name="clear", description="Removes specified amount of messages. By default 5.", guild_ids=config.DEBUG["test_guilds"])
    async def clear(self, interaction: Interaction, amount: int = 5):
        
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Failed. Invalid amount.", ephemeral=True)
            return
        
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"✅ Successfully removed {len(deleted)} messages.", ephemeral=True)

    
    @slash_command(name="avatar", description="Shows user's profile image.")
    async def avatar(self, interaction: Interaction, user: User = None):

        if user is None:
            user = interaction.user

        embed: Embed = Embed(title=f"{user.name}'s profile image", color=user.color)
        embed.set_image(user.avatar.url)
        embed.add_field(name="",value=f"[Download]({user.avatar.url})")

        await interaction.response.send_message(embed=embed)


def load(client):
    client.add_cog(Utilities(client))