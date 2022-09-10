import sys, nextcord
from nextcord.ext import commands
from nextcord import slash_command, Embed, Interaction, Member

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import long_datetime, complete_name

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()


class Info(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="Show information about a user. If no target is specified target will be author.", force_global=PRODUCTION)
    async def user_info(self, interaction: Interaction, user: Member = None):
        # Log
        log_message = complete_name(interaction.user) + " has called command: user_info."
        
        if user != None:
            log_message += " " + user.name
        self.logger.log_info(log_message + ".")

        # Get user
        target: Member = user or await interaction.guild.fetch_member(interaction.user.id)
        
        # Create message
        embed: Embed = Embed(title=target.name + "#" + target.discriminator, color=0xFBCE9D)
        embed.set_thumbnail(target.avatar.url)

        embed.add_field(name="ID:", value=target.id, inline=False)
        embed.add_field(name="Created:", value=long_datetime(target.created_at), inline=True)
        embed.add_field(name="Joined:", value=long_datetime(target.joined_at), inline=False)
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @slash_command(guild_ids=TEST_GUILDS, description="Says when a member joined.", force_global=PRODUCTION)
    async def joined(self, interaction: Interaction, member: nextcord.Member = None):
        # Log
        log_message = complete_name(interaction.user)  + " has called command: joined."

        if member != None:
            log_message += " " + member.name
        self.logger.log_info(log_message + ".")

        user: Member = member or interaction.user
        await interaction.response.send_message(user.name + " joined " + long_datetime(user.joined_at) + ".", ephemeral=True)
    

    @slash_command(guild_ids=TEST_GUILDS, description="Show info about me.", force_global=PRODUCTION)
    async def nosbot(self, interaction: Interaction):
        self.logger.log_info(complete_name(interaction.user)  + " has called command: nosbot.")

        # Create embed
        embed: Embed = Embed(title="NosBot", description="A multipurpose Discord bot.", color=0xFBCE9D)
        embed.set_thumbnail("https://raw.githubusercontent.com/4lt3rnative/nosbot/main/nosbot.png")

        embed.add_field(name="You can use me to:", value="🎮 **Play games\n👮‍♂️ Moderate your guild\n📊 Create polls\n🏷️ Create role givers\n📝 Create embeds\n🎛️ Use sound board\n... And more!**", inline=False)
        embed.add_field(name="Use /commands for list of all commands. Use /help to show the actions of commands.", value="Thank you for using me!", inline=False)

        await interaction.response.send_message(embed=embed)
    

def load(client: commands.Bot):
    client.add_cog(Info(client))