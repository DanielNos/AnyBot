import sys
from nextcord.ext import commands
from nextcord import Embed, Member, Interaction, slash_command

sys.path.append("../NosBot")
import logger as log
import dataManager

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()


class Profiles(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="Show users NosBot profile.", force_global=PRODUCTION)
    async def profile(self, interaction: Interaction, user: Member = None):
        member = user or interaction.user
        
        # Log
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: profile " + member.name + "#" + member.discriminator + ".")

        # Load profile
        profile = dataManager.load_profile(member)

        # Create embed
        embed: Embed = Embed(title=member.name + "#" + member.discriminator, description="NosBot Profile", color=0xFBCE9D)
        embed.set_thumbnail(member.avatar.url)

        games = profile["games"]

        hangman = "Win Rate: " + get_win_rate(games["hangman"]) + "\nGames Played: " + str(games["hangman"]["played"])
        embed.add_field(name="Hangman", value=hangman)

        tictactoe = "Win Rate: " + get_win_rate(games["tictactoe"]) + "\nGames Played: " + str(games["tictactoe"]["played"])
        embed.add_field(name="Tic-Tac-Toe", value=tictactoe)

        await interaction.response.send_message(embed=embed, ephemeral=True)


def get_win_rate(game: dict) -> str:
    return str(round((game["won"] / game["played"]) * 10000.0) / 100.0) + " %"


def load(client: commands.Bot):
    client.add_cog(Profiles(client))