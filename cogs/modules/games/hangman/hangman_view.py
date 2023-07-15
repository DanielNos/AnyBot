from typing import Dict
from nextcord.ui import View, Button
from nextcord import ButtonStyle, Interaction
from logging import Logger, getLogger
from hangman_modals import HangmanAddPlayer, HangmanInput
from hangman_game import Game


class HangmanView(View):
    def __init__(self, users_in_games: Dict[int, Game]):
        super().__init__()
        self.logger: Logger = getLogger("bot")
        self.users_in_games = users_in_games
    
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
        await interaction.response.send_modal(HangmanInput(True, self.users_in_games))
    
    
    async def guess_expression(self, interaction: Interaction):
        await interaction.response.send_modal(HangmanInput(False, self.users_in_games))
    

    async def add_player(self, interaction: Interaction):

        # User isn't in this game
        if interaction.user.id not in self.users_in_games:
            await interaction.response.defer()
            return
        
        game: Game = self.users_in_games[interaction.user.id]

        # User isn't games creator
        if game.creator.id != interaction.user.id:
            await interaction.response.send_message("❌ You have to be the games creator to add players to it.", ephemeral=True)
            return

        await interaction.response.send_modal(HangmanAddPlayer(self.users_in_games))


    async def leave(self, interaction: Interaction):

        # Return if user isn't in a game
        if not interaction.user.id in self.users_in_games.keys():
            await interaction.response.send_message("❌ You aren't in a game.", ephemeral=True)
            return

        game: Game = self.users_in_games[interaction.user.id]

        self.logger.info(f"{interaction.user.name} has left a game of Hangman ({game.message.id}).")

        # Remove game if user is it's creator
        if game.creator.id == interaction.user.id:
            await game.message.delete()
            game.delete()
            await interaction.response.send_message(f"ℹ️ {game.creator.name} has deleted his game of hangman.")
            return

        # Remove player
        game.players.remove(interaction.user)
        await game.message.edit(embed=game.create_embed())
        await interaction.response.send_message(f"ℹ️ {interaction.user.name} has left {game.creator.name}'s game of Hangman ({game.message.id}).", delete_after=3)