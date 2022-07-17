import sys, nextcord
from nextcord.ext import commands
from nextcord import slash_command, Embed, Interaction, Member

sys.path.append("../NosBot")
import logger as log

TEST_GUILDS = []
logger = None

class Info(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="Show information about a user. If no target is specified target will be author.", force_global=True)
    async def user_info(self, interaction: Interaction, user: Member = None):
        # Log
        log_message = interaction.user.name + "#" + interaction.user.discriminator + " has called command: user_info"
        if user != None:
            log_message += " " + user.name
        logger.log_info(log_message + ".")

        # Get user
        target: Member = user or await interaction.guild.fetch_member(interaction.user.id)
        
        # Create message
        embed: Embed = Embed(title=target.name + "#" + target.discriminator, color=0xFBCE9D)
        embed.set_thumbnail(target.avatar.url)

        embed.add_field(name="ID:", value=target.id, inline=False)
        embed.add_field(name="Created:", value=target.created_at.strftime("%d-%m-%Y %H:%M:%S"), inline=True)
        embed.add_field(name="Joined:", value=target.joined_at.strftime("%d-%m-%Y %H:%M:%S"), inline=False)
        embed.add_field(name="Nickname:", value=target.nick, inline=True)
        embed.add_field(name="Is Bot:", value=target.bot, inline=True)

        roles = ""
        for role in target.roles:
            if role.name != "@everyone":
                roles += role.mention + ", "
        roles = roles.removesuffix(", ")

        if roles == "":
            roles = "None"

        embed.add_field(name="Roles:", value=roles, inline=False)
        
        await interaction.response.send_message(embed=embed)


    @slash_command(guild_ids=TEST_GUILDS, description="Says when a member joined.", force_global=True)
    async def joined(self, interaction: Interaction, member: nextcord.Member = None):
        # Log
        log_message = interaction.user.name + "#" + interaction.user.discriminator + " has called command: joined"
        if member != None:
            log_message += " " + member.name
        logger.log_info(log_message + ".")

        user: Member = member or interaction.user
        await interaction.response.send_message(user.name + " joined in " + user.joined_at.strftime("%d-%m-%Y %H:%M:%S") + ".")
    


def load(client: commands.Bot):
    client.add_cog(Info(client))