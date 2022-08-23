import sys
from unidecode import unidecode
from nextcord.ext import commands
from nextcord.ui import View, Button, Modal, TextInput
from nextcord import slash_command, ButtonStyle, SlashOption, PartialInteractionMessage, Interaction, Member, Embed, Message, User, RawMessageDeleteEvent, RawBulkMessageDeleteEvent
from random import choice

sys.path.append("../../NosBot")
import dataManager, emojiDict, access
import logger as log
from formatting import complete_name

LETTERS = list("abcdefghijklmnopqrstuvwxyz")
ALLOWED_CHARS = "&:-' "
PLAYER_ADD_IDT = 5
GUESS_IDT = 5
PLAYER_LEAVE_IDT = 10
INCORRECT_GUESS_IDT = 5
CORRECT_GUESS_IDT = 10

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()
PACKS = dataManager.load_hangman_packs()

users_in_games = {}
game_messages = {}


class Controls(View):
    def __init__(self, client: commands.Bot, logger: log.Logger):
        super().__init__()
        self.client = client
        self.logger = logger
    
        # Create buttons
        button: Button = Button(style=ButtonStyle.blurple, label="Guess Letter")
        button.callback = self.guess_letter
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.blurple, label="Guess Expression")
        button.callback = self.guess_expression
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.gray, label="Add Player")
        button.callback = self.add_player
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.red, label="Leave")
        button.callback = self.leave
        self.add_item(button)


    async def guess_letter(self, interaction: Interaction):
        await interaction.response.send_modal(HangmanInput(logger=self.logger, letter=True))
    
    
    async def guess_expression(self, interaction: Interaction):
        await interaction.response.send_modal(HangmanInput(logger=self.logger, letter=False))
    

    async def add_player(self, interaction: Interaction):
        await interaction.response.send_modal(HangmanAddPlayer(logger=self.logger))


    async def leave(self, interaction: Interaction):
        self.logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman leave.")

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


class HangmanAddPlayer(Modal):
    def __init__(self, logger: log.Logger):
        super().__init__(title="Add Player")
        self.logger = logger

        self.user = TextInput(label="User Name:", min_length=1, max_length=50)
        self.add_item(self.user)
    

    async def callback(self, interaction: Interaction):
        members = interaction.guild.members
        user = self.user.value

        for member in members:
            member: Member = member
            if user.lower() in [member.display_name.lower(), member.name.lower()] or complete_name(member).lower() == user.lower():
                await self.add_player(interaction, member)
                return

        await interaction.response.defer()
    
    async def add_player(self, interaction: Interaction, player: Member):
        self.logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman add_player " + player.name + "#" + player.discriminator + ".")
        
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
        await interaction.response.send_message("ℹ️ " + complete_name(player) + " was added to " + game.creator.name + "'s game of hangman.", delete_after=PLAYER_ADD_IDT)

    

class HangmanInput(Modal):
    def __init__(self, logger: log.Logger, letter: bool):
        super().__init__(title=("Guess Letter" * letter) + ("Guess Expression" * (not letter)))
        self.letter = letter
        self.logger = logger

        if letter:
            self.text = TextInput(label="Letter:", min_length=1, max_length=1)
        else:
            self.text = TextInput(label="Expression:", min_length=1, max_length=100)
        self.add_item(self.text)
    

    async def callback(self, interaction: Interaction):
        if self.letter:
            await self.guess_letter(interaction, self.text.value)
        else:
            await self.guess_expression(interaction, self.text.value)
    

    async def guess_letter(self, interaction: Interaction, letter: str):
        self.logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman guess " + letter + ".")

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

            # Add experience
            for player in game.players:
                dataManager.add_game_record(player.id, "hangman", False)

            # Delete game
            game.delete()
            return
        
        # Check for victory
        if game.check_for_victory():
            # Add experience
            for player in game.players:
                if player.id != interaction.user.id:
                    dataManager.add_game_record(player.id, "hangman", False)
            dataManager.add_game_record(interaction.user.id, "hangman", True)

            # Update game message
            embed = normal_embed
            embed.add_field(name=interaction.user.name + "#" + interaction.user.discriminator + " has won!", value="Congratulations!", inline=False)
            await game.message.edit(embed=embed, view=None)

            # Delete game
            game.delete()
            return

        # Update game message
        await game.message.edit(embed=normal_embed)
    

    async def guess_expression(self, interaction: Interaction, expression: str):
        self.logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman guess_expression " + expression + ".")

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

        # INCORRECT GUESS
        if game.expression.lower() != legal_expression:
            game.wrong_guesses += 1
            await game.message.edit(embed=game.create_embed())
            await interaction.response.send_message("ℹ️ " + interaction.user.name + " has incorrectly guessed the expression \"" + legal_expression.upper() + "\".", delete_after=INCORRECT_GUESS_IDT)
            return
            
        # CORRECT GUESS
        # Add experience
        for player in game.players:
            if player.id != interaction.user.id:
                dataManager.add_game_record(player.id, "hangman", False)
        dataManager.add_game_record(interaction.user.id, "hangman", True)

        # Edit embed
        embed: Embed = game.message.embeds[0]
        embed.add_field(name=interaction.user.name + "#" + interaction.user.discriminator + " has won!", value="Congratulations!", inline=False)

        game.letters = [True]*len(LETTERS)
        new_embed = game.create_embed()

        embed.set_field_at(0, name=embed.fields[0].name, value=new_embed.fields[0].value, inline=False)

        # Edit message
        await game.message.edit(embed=embed, view=None)
        await interaction.response.send_message("ℹ️ " + interaction.user.name + " has correctly guessed the expression \"" + legal_expression.upper() + "\".", delete_after=CORRECT_GUESS_IDT)
        game.delete()


class Game:
    def __init__(self, creator: User, expression: str):
        self.message: Message = None
        self.creator: User = creator
        self.expression: str = expression.upper()

        self.players = []
        self.letters = [False] * len(LETTERS)
        self.wrong_guesses = 0
    

    def create_embed(self) -> Embed:
        embed: Embed = Embed(title="Hangman", color=0xFBCE9D)

        # Expression
        expression = "```\n"
        for i in range(len(self.expression)):
            if self.expression[i] in ALLOWED_CHARS:
                expression += self.expression[i] + " "
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
        embed.set_thumbnail("https://raw.githubusercontent.com/4lt3rnative/nosbot/main/hangman" + str(self.wrong_guesses) + ".png")

        # Creator
        embed.set_footer(text="Creator: " + self.creator.name + "#" + self.creator.discriminator)
        
        return embed
    

    def delete(self):
        global users_in_games
        for player in self.players:
            users_in_games.pop(player.id)
        
        if self.message.id in game_messages.keys():
            game_messages.pop(self.message.id)
        if self.message.id in users_in_games.keys():
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
            if letter in used_letters or letter in ALLOWED_CHARS:
                complete_expression += letter
        
        return complete_expression == self.expression.lower()


class Hangman(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="none", force_global=PRODUCTION)
    async def hangman(self, interaction: Interaction):
        return


    async def start_game(self, interaction: Interaction, expression: str, from_pack = False):
        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Start Games"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to start games.", ephemeral=True)
            return

        # Return if user is in a game
        if interaction.user.id in users_in_games.keys():
            await interaction.response.send_message("🚫 Failed. You are already in a game of hangman. You can leave it using /hangman leave.", ephemeral=True)
            return

        # Create game
        game = Game(interaction.user, expression)
        if from_pack:
            game.players.append(interaction.user)

        response: PartialInteractionMessage = await interaction.response.send_message(embed=game.create_embed(), view=Controls(self.client, self.logger))
        game.message = await response.fetch()
        
        users_in_games[interaction.user.id] = game
        game_messages[game.message.id] = game.creator.id


    @hangman.subcommand(description="Start a game of hangman.")
    async def start(self, interaction: Interaction, expression: str):
        self.logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman start " + expression + ".")

        # Remove illegal characters from expression
        legal_expression = ""
        for ch in unidecode(expression.lower()):
            if ch in ("abcdefghijklmnopqrstuvwxyz" + ALLOWED_CHARS):
                legal_expression += ch
        
        # Create game if expression is long enough
        if len(legal_expression) > 0:
            await self.start_game(interaction, legal_expression)
        else:
            await interaction.response.send_message("🚫 Failed. Expression was too short or contained illegal characters.",ephemeral=True)
    
    
    @hangman.subcommand(description="Start a game of hangman.")
    async def start_expression_pack(self, interaction: Interaction, expression_pack: str = SlashOption(choices=PACKS.keys())):
        self.logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: hangman start_expression_pack " + expression_pack + ".")
        
        await self.start_game(interaction, choice(PACKS[expression_pack]), True)

    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in game_messages.keys():
            self.logger.log_info("Hangman " + str(event.message_id) + " message was deleted. Removing game instance.")

            users_in_games[game_messages[event.message_id]].delete()
    

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, event: RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in game_messages.keys():
                self.logger.log_info("Hangman " + str(id) + " message was deleted. Removing game instance.")

                users_in_games[game_messages[id]].delete()


def load(client: commands.Bot):
    client.add_cog(Hangman(client))