import sys
from unidecode import unidecode
from nextcord.ext import commands
from nextcord import PartialInteractionMessage, slash_command, Interaction, Member, Embed, Message, User, RawMessageDeleteEvent, RawBulkMessageDeleteEvent

sys.path.append("../../NosBot")
import dataManager, emojiDict, access
import logger as log

LETTERS = list("abcdefghijklmnopqrstuvwxyz")
PLAYER_ADD_IDT = 5
GUESS_IDT = 5
PLAYER_LEAVE_IDT = 10
INCORRECT_GUESS_IDT = 5
CORRECT_GUESS_IDT = 10

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

logger = None

users_in_games = {}
game_messages = {}

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

        # Expression
        expression = "```\n"
        for i in range(len(self.expression)):
            if self.expression[i] == " ":
                expression += "  "
            else:
                if not self.letters[LETTERS.index(self.expression[i].lower())]:
                    expression += "_ "
                else:
                    expression += self.expression[i] + " "

        embed.add_field(name="Expression:", value=expression[:-1] + "\n```", inline=False)

        # Letters
        letters = ""
        for i in range(len(LETTERS)):
            if not self.letters[i]:
                letters += emojiDict.LETTERS[i] + " "
            else:
                letters += LETTERS[i].upper() + " "

        embed.add_field(name="Letters:", value=letters[:-1], inline=False)

        # Players
        players = ""
        for player in self.players:
            players += player.mention + " "
        
        if players == "":
            players = "none "

        embed.add_field(name="Players:", value=players[:-1], inline=False)

        # Icon
        embed.set_thumbnail("https://raw.githubusercontent.com/DanielNos/NosBot/main/icons/hangman" + str(self.wrong_guesses) + ".png")

        # Creator
        embed.set_footer(text="Creator: " + self.creator.name + "#" + self.creator.discriminator)
        
        return embed
    

    def delete(self):
        global users_in_games
        for player in self.players:
            users_in_games.pop(player.id)
        
        game_messages.pop(self.message.id)
        users_in_games.pop(self.creator.id)
    
    
    def check_for_victory(self) -> bool:
        # Get all the correctly guessed letters
        used_letters = ""
        for i in range(len(LETTERS)):
            if self.letters[i]:
                used_letters += LETTERS[i]
        
        # Try to recreate expression with guessed letters
        complete_expression = ""
        for letter in self.expression.lower():
            if letter in used_letters or letter == " ":
                complete_expression += letter
        
        return complete_expression == self.expression.lower()


class Hangman(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="none", force_global=PRODUCTION)
    async def hangman(self, interaction: Interaction):
        return

    
    @hangman.subcommand(description="Leave a game of hangman.")
    async def leave(self, interaction: Interaction):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman leave.")

        # Return if user isn't in a game
        if not interaction.user.id in users_in_games.keys():
            await interaction.response.send_message("🚫 Failed. You aren't in a game.", ephemeral=True)
            return

        game: Game = users_in_games[interaction.user.id]

        # Remove game if user is it's creator
        if game.creator.id == interaction.user.id:
            await game.message.delete()
            game.delete()
            await interaction.response.send_message("ℹ️ " + game.creator.name + "#" + game.creator.discriminator + " has deleted his game of hangman.")
            return

        # Remove player
        game.players.remove(interaction.user)
        await game.message.edit(embed=game.create_embed())
        await interaction.response.send_message("ℹ️ " + interaction.user.name + "#" + interaction.user.discriminator + " has left " + game.creator.name + "'s game of hangman.", delete_after=PLAYER_LEAVE_IDT)


    @hangman.subcommand(description="Start a game of hangman.")
    async def start(self, interaction: Interaction, expression: str):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman start " + expression + ".")

        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Start Games"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to start games.", ephemeral=True)
            return

        # Return if user is in a game
        if interaction.user.id in users_in_games.keys():
            await interaction.response.send_message("🚫 Failed. You are already in a game of hangman. You can leave it using /hangman leave.", ephemeral=True)
            return

        # Remove illegal characters from expression
        legal_expression = ""
        for ch in unidecode(expression):
            if ch in "abcdefghijklmnopqrstuvwxyz ":
                legal_expression += ch

        # Create game
        game = Game(interaction.user, legal_expression)

        response: PartialInteractionMessage = await interaction.response.send_message(embed=game.create_embed())

        game.message = await response.fetch()
        users_in_games[interaction.user.id] = game
        game_messages[game.message.id] = game.creator.id
    

    @hangman.subcommand(description="Guess a letter in a game of hangman.")
    async def guess(self, interaction: Interaction, letter: str):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman guess " + letter + ".")

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
        
        # Flip letter
        game.letters[LETTERS.index(letter)] = True
        if not letter in game.expression.lower():
            game.wrong_guesses += 1

        await interaction.response.send_message("ℹ️ " + interaction.user.name + "#" + interaction.user.discriminator + " has guessed the letter " + letter.upper() + ".", delete_after=GUESS_IDT)

        normal_embed: Embed = game.create_embed()

        # Check for game over
        if game.wrong_guesses >= 11:
            # Show the answer
            game.letters = [True]*len(LETTERS)

            embed: Embed = normal_embed
            embed.add_field(name="GAME OVER!", value="Nobody won.")
            embed.set_field_at(1, name=embed.fields[1].name, value=normal_embed.fields[1].value, inline=False)

            await game.message.edit(embed=embed)

            # Delete game
            game.delete()
            return
        
        # Check for victory
        if game.check_for_victory():
            # Update game message
            embed = normal_embed
            embed.add_field(name=interaction.user.name + "#" + interaction.user.discriminator + " has won!", value="Congratulations!", inline=False)
            await game.message.edit(embed=embed)

            # Delete game
            game.delete()
            return

        # Update game message
        await game.message.edit(embed=normal_embed)
        

    @hangman.subcommand(description="Add player to your game of hangman.")
    async def add_player(self, interaction: Interaction, player: Member):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman add_player " + player.name + "#" + player.discriminator + ".")
        
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
        
        # Return if user is player
        if player.id == interaction.user.id:
            await interaction.response.send_message("🚫 Failed. You can't add yourself to the game.", ephemeral=True)
            return
        
        # Return if player is a bot
        if player.bot:
            await interaction.response.send_message("🚫 Failed. You can't add bots to this game.", ephemeral=True)
            return

        # Add player
        game.players.append(player)
        users_in_games[player.id] = game
        await game.message.edit(embed=game.create_embed())
        await interaction.response.send_message("ℹ️ " + player.name + "#" + player.discriminator + " was added to " + game.creator.name + "'s game of hangman.", delete_after=PLAYER_ADD_IDT)


    @hangman.subcommand(description="Add player to your game of hangman.")
    async def guess_expression(self, interaction: Interaction, expression: str):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman guess_expression " + expression + ".")

        # Return if user isn't in a game
        if not interaction.user.id in users_in_games.keys():
            await interaction.response.send_message("🚫 Failed. You aren't currently in a game of hangman.", ephemeral=True)
            return

        # Remove illegal characters from expression
        legal_expression = ""
        for ch in unidecode(expression.lower()):
            if ch in "abcdefghijklmnopqrstuvwxyz ":
                legal_expression += ch
        
        game: Game = users_in_games[interaction.user.id]

        # Incorrect guess
        if game.expression.lower() != legal_expression:
            game.wrong_guesses += 1
            await game.message.edit(embed=game.create_embed())
            await interaction.response.send_message("ℹ️ " + interaction.user.name + " has incorrectly guessed the expression \"" + legal_expression.upper() + "\".", delete_after=INCORRECT_GUESS_IDT)
            return
        
        # Correct guess
        # Edit embed
        embed: Embed = game.message.embeds[0]
        embed.add_field(name=interaction.user.name + "#" + interaction.user.discriminator + " has won!", value="Congratulations!", inline=False)

        game.letters = [True]*len(LETTERS)
        new_embed = game.create_embed()

        embed.set_field_at(0, name=embed.fields[0].name, value=new_embed.fields[0].value, inline=False)

        # Edit message
        await game.message.edit(embed=embed)
        await interaction.response.send_message("ℹ️ " + interaction.user.name + " has correctly guessed the expression \"" + legal_expression.upper() + "\".", delete_after=CORRECT_GUESS_IDT)
        game.delete()

    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in game_messages.keys():
            logger.log_info("Hangman " + str(event.message_id) + " message was deleted. Removing game instance.")

            users_in_games[game_messages[event.message_id]].delete()
    

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, event: RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in game_messages.keys():
                logger.log_info("Hangman " + str(id) + " message was deleted. Removing game instance.")

                users_in_games[game_messages[id]].delete()


def load(client: commands.Bot):
    client.add_cog(Hangman(client))