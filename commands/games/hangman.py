from mimetypes import guess_all_extensions
import sys
from numpy import delete
from unidecode import unidecode
from nextcord.ext import commands
from nextcord import PartialInteractionMessage, slash_command, Interaction, SlashOption, Member, Embed, Message, User

sys.path.append("../../NosBot")
import dataManager, emojiDict
import logger as log

LETTERS = list("abcdefghijklmnopqrstuvwxyz")
PLAYER_ADD_IDT = 5
GUESS_IDT = 5

TEST_GUILDS = []
HANGMAN_ICONS = []
logger = None

users_in_games = {}

class Game:
    def __init__(self, creator: User, expression: str):
        self.message: Message = None
        self.creator: User = creator
        self.expression: str = expression.upper()

        self.players = []
        self.letters = [False]*len(LETTERS)
        self.wrong_guesses = 0
    

    def create_embed(self) -> Embed:
        embed: Embed = Embed(title="Hangman", color=0xFBCE9D)

        # Word
        word = "`"
        for i in range(len(self.expression)):
            if self.expression[i] == " ":
                word += "  "
            else:
                if not self.letters[LETTERS.index(self.expression[i].lower())]:
                    word += "_ "
                else:
                    word += self.expression[i] + " "

        embed.add_field(name="Word:", value=word[:-1] + "`", inline=False)

        # Letters
        letters = ""
        for i in range(len(LETTERS)):
            if not self.letters[i]:
                letters += emojiDict.LETTERS[i] + " "
            else:
                letters += LETTERS[i].upper() + " "

        embed.add_field(name="Letters:", value=letters[:-1], inline=False)

        # Guesses
        embed.add_field(name="Guesses:", value=(":red_square:" * self.wrong_guesses) + (":white_small_square:" * (11 - self.wrong_guesses)))
        
        # Players
        players = ""
        for player in self.players:
            players += player.mention + " "
        
        if players == "":
            players = "none "

        embed.add_field(name="Players:", value=players[:-1], inline=False)

        return embed



class Hangman(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")
    

    @commands.Cog.listener()
    async def on_ready(self):
        global TEST_GUILDS
        TEST_GUILDS = dataManager.load_test_guilds()
    

    @slash_command(guild_ids=TEST_GUILDS, description="none", force_global=True)
    async def hangman(self, interaction: Interaction):
        return

    
    @hangman.subcommand(description="Leave a game of hangman.")
    async def leave(self, interaction: Interaction):
        # Return if user isn't in a game
        if not interaction.user.id in users_in_games.keys():
            await interaction.response.send_message("🚫 Failed. You aren't in a game.")
            return


    @hangman.subcommand(description="Start a game of hangman.")
    async def start(self, interaction: Interaction, expression: str):
        # Return if user is in a game
        if interaction.user.id in users_in_games.keys():
            await interaction.response.send_message("🚫 Failed. You are already in a game of hangman. You can leave it using /hangman leave.")
            return

        game = Game(interaction.user, expression)

        response: PartialInteractionMessage = await interaction.response.send_message(embed=game.create_embed())

        game.message = await response.fetch()
        users_in_games[interaction.user.id] = game
    

    @hangman.subcommand(description="Guess a letter in a game of hangman.")
    async def guess(self, interaction: Interaction, letter: str):
        # Return if user isn't in a game
        if not interaction.user.id in users_in_games.keys():
            await interaction.response.send_message("🚫 Failed. You aren't currently in a game of hangman.", ephemeral=True)
            return

        letter = unidecode(letter[0].lower())
        
        # Return if input isn't a letter
        if not letter in LETTERS:
            await interaction.response.send_message(f"🚫 Failed. '{letter.upper()}' is not a valid letter.", ephemeral=True)
            return
        
        game: Game = users_in_games[interaction.user.id]

        # Return if letter was already guessed
        for i in range(len(LETTERS)):
            if game.letters[i] and LETTERS[i] == letter:
                await interaction.response.send_message(f"🚫 Failed. '{letter.upper()}' has been already guessed.", ephemeral=True)
                return
        
        # Flip letter/s
        game.letters[LETTERS.index(letter)] = True
        if not letter in game.expression.lower():
            game.wrong_guesses += 1
        
        await game.message.edit(embed=game.create_embed())
        await interaction.response.send_message("ℹ️ " + interaction.user.name + "#" + interaction.user.discriminator + " has guessed the letter " + letter.upper() + ".", delete_after=GUESS_IDT)
        

    @hangman.subcommand(description="Add player to your game of hangman.")
    async def add_player(self, interaction: Interaction, player: Member):
        # Return if user isn't in a game
        if not interaction.user.id in users_in_games.keys():
            await interaction.response.send_message("🚫 Failed. You aren't currently in a game of hangman.", ephemeral=True)
            return
        
        game: Game = users_in_games[interaction.user.id]

        # Return if user isn't games creator
        if game.creator.id != interaction.user.id:
            await interaction.response.send_message("🚫 Failed. You have to be the games creator to add players to it.", ephemeral=True)
            return
        
        # Return if player is already in the game
        if player in game.players:
            await interaction.response.send_message("🚫 Failed. Player is already in the game.", ephemeral=True)
            return
        
        # Return if player is a bot
        if player.bot:
            await interaction.response.send_message("🚫 Failed. You can't add bots to this game.", ephemeral=True)
            return

        # Add player
        game.players.append(player)
        await game.message.edit(embed=game.create_embed())
        await interaction.response.send_message("ℹ️ " + player.name + "#" + player.discriminator + " was added to " + game.creator.name + "s game of hangman.", delete_after=PLAYER_ADD_IDT)


def load(client: commands.Bot):
    client.add_cog(Hangman(client))