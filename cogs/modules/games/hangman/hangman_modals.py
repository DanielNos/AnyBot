from typing import Dict
from nextcord.ui import Modal, TextInput
from nextcord import Interaction, Member, Embed
from logging import Logger, getLogger
from unidecode import unidecode
from formatting import LETTERS
from hangman_game import Game


class HangmanInput(Modal):
    def __init__(self, letter: bool, users_in_games: Dict[int, Game]):
        super().__init__(title=("Guess Letter" * letter) + ("Guess Expression" * (not letter)))
        self.logger: Logger = getLogger("bot")

        self.users_in_games = users_in_games
        self.letter = letter

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
        # Return if user isn't in a game
        if not interaction.user.id in self.users_in_games.keys():
            await interaction.response.send_message("❌ You aren't currently in a game of hangman.", ephemeral=True)
            return

        letter = unidecode(letter[0].lower())
        
        # Return if input isn't a letter
        if not letter in LETTERS:
            await interaction.response.send_message(f"❌ '{letter.upper()}' is not a valid letter.", ephemeral=True)
            return
        
        game: Game = self.users_in_games[interaction.user.id]

        self.logger.info(f"{interaction.user.name} has guessed the letter {letter} in a game ({game.message.id}).")

        # Return if letter was already guessed
        for i in range(len(LETTERS)):
            if game.letters[i] and LETTERS[i] == letter:
                await interaction.response.send_message(f"❌ '{letter.upper()}' has been already guessed.", ephemeral=True)
                return
        
        # Flip letter
        game.letters[LETTERS.index(letter)] = True
        if not letter in game.expression.lower():
            game.wrong_guesses += 1

        await interaction.response.send_message(f"ℹ️ {interaction.user.name} has guessed the letter {letter.upper()}.", delete_after=3)

        normal_embed: Embed = game.create_embed()

        # Check for game over
        if game.wrong_guesses >= 11:
            # Show the answer
            game.letters = [True]*len(LETTERS)

            embed: Embed = normal_embed
            embed.add_field(name="GAME OVER!", value="Nobody won.")
            embed.set_field_at(1, name=embed.fields[1].name, value=normal_embed.fields[1].value, inline=False)

            await game.message.edit(embed=embed, view=None)

            # Delete game
            game.delete()
            return
        
        # Check for victory
        if game.check_for_victory():

            # Update game message
            embed = normal_embed
            embed.add_field(name=f"{interaction.user.name} has won!", value="Congratulations!", inline=False)
            await game.message.edit(embed=embed, view=None)

            # Delete game
            game.delete()
            return

        # Update game message
        await game.message.edit(embed=normal_embed)
    

    async def guess_expression(self, interaction: Interaction, expression: str):

        # Return if user isn't in a game
        if not interaction.user.id in self.users_in_games.keys():
            await interaction.response.send_message("❌ You aren't currently in a game of hangman.", ephemeral=True)
            return

        # Remove illegal characters from expression
        legal_expression = ""
        for ch in unidecode(expression.lower()):
            if ch in "abcdefghijklmnopqrstuvwxyz ":
                legal_expression += ch
        
        game: Game = self.users_in_games[interaction.user.id]
        self.logger.info(f"{interaction.user.name} has guessed expression \"{expression}\" in a game ({game.message.id}).")

        # INCORRECT GUESS
        if game.expression.lower() != legal_expression:
            game.wrong_guesses += 1
            await game.message.edit(embed=game.create_embed())
            await interaction.response.send_message(f"ℹ️ {interaction.user.name} has incorrectly guessed the expression \"{legal_expression.upper()}\".", delete_after=3)
            return
            
        # CORRECT GUESS
        # Edit embed
        embed: Embed = game.message.embeds[0]
        embed.add_field(name=f"{interaction.user.name} has won!", value="Congratulations!", inline=False)

        game.letters = [True]*len(LETTERS)
        new_embed = game.create_embed()

        embed.set_field_at(0, name=embed.fields[0].name, value=new_embed.fields[0].value, inline=False)

        # Edit message
        await game.message.edit(embed=embed, view=None)
        await interaction.response.send_message(f"ℹ️ {interaction.user.name} has correctly guessed the expression \"{legal_expression.upper()}\".", delete_after=3)
        game.delete()


class HangmanAddPlayer(Modal):
    def __init__(self, users_in_games):
        super().__init__(title="Add Player")
        self.logger: Logger = getLogger("bot")
        self.users_in_games = users_in_games

        self.user = TextInput(label="User Name:", min_length=1, max_length=50)
        self.add_item(self.user)
    

    async def callback(self, interaction: Interaction):
        members = interaction.guild.members
        user = self.user.value

        for member in members:
            member: Member = member
            if user.lower() in [member.display_name.lower(), member.name.lower()]:
                await self.add_player(interaction, member)
                return

        await interaction.response.defer()
    

    async def add_player(self, interaction: Interaction, player: Member):
        
        # Return if user is in a game already
        if not interaction.user.id in self.users_in_games.keys():
            await interaction.response.send_message("❌ You aren't currently in a game of hangman.", ephemeral=True)
            return
        
        game: Game = self.users_in_games[interaction.user.id]
        
        # Return if player is already in the game
        if player in game.players:
            await interaction.response.send_message("❌ Player is already in the game.", ephemeral=True)
            return
        
        # Return if user is player
        if player.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't add yourself to the game.", ephemeral=True)
            return
        
        # Return if player is a bot
        if player.bot:
            await interaction.response.send_message("❌ You can't add bots to this game.", ephemeral=True)
            return

        # Add player
        game.players.append(player)
        self.users_in_games[player.id] = game
        await game.message.edit(embed=game.create_embed())
        await interaction.response.send_message(f"ℹ️ {player} was added to {game.creator.name}'s game of hangman.", delete_after=3)

        self.logger.info(f"{interaction.user.name} has added player {player.name} to {game.creator.name}'s game ({game.message.id}).")