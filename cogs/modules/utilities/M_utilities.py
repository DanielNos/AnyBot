import logging, datetime
from logging import Logger
from nextcord import Interaction, Member, Embed, slash_command
from nextcord.ext.commands import Cog, Bot
import config


def format_datetime(obj: datetime.datetime) -> str:
        if obj.microsecond >= 500_000:
            obj += datetime.timedelta(seconds=1)

        obj.replace(microsecond=0)
        parts = str(obj)[:-6].split(" ")
        
        return parts[0] + "\n" + parts[1]


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

        self.logger.info(f"{interaction.user.name} has cleared {amount} messages in {interaction.guild.name}/{interaction.channel.name}.")
    

    @slash_command(name="avatar", description="Shows user's profile image.", guild_ids=config.DEBUG["test_guilds"])
    async def avatar(self, interaction: Interaction, user: Member = None):

        # No target
        if user is None:
            user = interaction.user

        # Create embed
        embed: Embed = Embed(title=f"{user.name}'s profile image", color=user.color)
        embed.set_image(user.avatar.url)
        embed.add_field(name="",value=f"[Download]({user.avatar.url})")

        await interaction.response.send_message(embed=embed)
        
        self.logger.info(f"{interaction.user.name} has shown avatar of user {user.name} in {interaction.guild.name}/{interaction.channel.name}.")

    
    @slash_command(name="info", description="Shows information about user.", guild_ids=config.DEBUG["test_guilds"])
    async def info(self, interaction: Interaction, user: Member = None):
        
        # No target
        if user is None:
            user = interaction.user

        # Create embed
        embed: Embed = Embed(title=f"{user.name} ({user.id})", color=user.color)
        embed.set_thumbnail(user.avatar.url)
        embed.add_field(name="Nickname:", value=user.display_name)

        roles = ""
        if len(user.roles) > 0:
            roles += user.roles[0].name

        for role in user.roles[1:]:
            roles += "\n" + role.name

        embed.add_field(name="Roles:", value=roles)
        
        if user.premium_since is not None:
            embed.add_field(name="Premium since:", value=format_datetime(user.premium_since))
        else:
            embed.add_field(name="Premium since:", value="never")

        embed.add_field(name="Created:", value=format_datetime(user.created_at))
        embed.add_field(name="Joined server:", value=format_datetime(user.joined_at))

        await interaction.response.send_message(embed=embed)

        self.logger.info(f"{interaction.user.name} has shown info about user {user.name} in {interaction.guild.name}/{interaction.channel.name}.")
    

def load(client):
    client.add_cog(Utilities(client))