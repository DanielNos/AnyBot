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
        profile = dataManager.load_profile(member.id)

        # Create embed
        embed: Embed = Embed(title=member.name + "#" + member.discriminator, description="Level: " + str(profile["level"]), color=0xFBCE9D)
        embed.set_thumbnail(member.avatar.url)

        # Experience
        embed.add_field(name="Experience:", value= progress_bar(profile["experience"], profile["required experience"]) + " " + str(profile["experience"]) + " / " + str(profile["required experience"]), inline=False)

        # Games
        games = profile["games"]

        embed.add_field(name="GAMES", value="Total played: " + str(games["hangman"]["played"] + games["tictactoe"]["played"]), inline=False)

        hangman = "Win Rate: " + get_win_rate(games["hangman"]) + "\nGames Played: " + str(games["hangman"]["played"])
        embed.add_field(name="Hangman", value=hangman)

        tictactoe = "Win Rate: " + get_win_rate(games["tictactoe"]) + "\nGames Played: " + str(games["tictactoe"]["played"])
        embed.add_field(name="Tic-Tac-Toe", value=tictactoe)

        flood = "Win Rate: " + get_win_rate(games["flood"]) + "\nGames Played: " + str(games["flood"]["played"])
        embed.add_field(name="Flood", value=flood)

        mastermind = "Win Rate: " + get_win_rate(games["mastermind"]) + "\nGames Played: " + str(games["mastermind"]["played"])
        embed.add_field(name="Mastermind", value=mastermind)

        await interaction.response.send_message(embed=embed, ephemeral=True)


def get_win_rate(game: dict) -> str:
    if game["played"] == 0:
        return "-"
    return str(round((game["won"] / game["played"]) * 10000.0) / 100.0) + " %"


def progress_bar(value: int = 0, max: int = 0) -> str:
    if max == 0 or value == 0:
        return "`" + (" " * 30)  +"`"

    percentage = round((value / max) * 30)

    return "`" + ("█" * percentage) + (" " * (30 - percentage)) + "`"


def load(client: commands.Bot):
    client.add_cog(Profiles(client))