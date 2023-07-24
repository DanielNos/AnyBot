import os, sys
sys.path.append(os.path.dirname(__file__))

from logging import Logger, getLogger
from unidecode import unidecode
from nextcord.ext.commands import Bot, Cog
from nextcord import slash_command, SlashOption, PartialInteractionMessage, Interaction, RawMessageDeleteEvent, RawBulkMessageDeleteEvent
from random import choice
from typing import Dict
from config import DEBUG
from hangman_view import HangmanView
from hangman_game import Game, ALLOWED_CHARS


# Load expression packs
PACKS = {}
for file_name in os.listdir("./modules_data/hangman/"):
    file = open("./modules_data/hangman/" + file_name, "r")
    lines = file.readlines()
    file.close()

    lines = [line[:-1] for line in lines]

    PACKS[file_name] = lines


class Hangman(Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.logger: Logger = getLogger("bot")

        self.users_in_games: Dict[int, Game] = {}
        self.game_messages: Dict[int, int] = {}

        self.logger.info(f"Loaded {len(PACKS)} expression packs.")    
    

    @slash_command(guild_ids=DEBUG["test_guilds"])
    async def hangman(self, interaction: Interaction):
        return


    async def start_game(self, interaction: Interaction, expression: str, from_pack = False):

        # Return if user is in a game
        if interaction.user.id in self.users_in_games.keys():
            game: Game = self.users_in_games[interaction.user.id]
            await interaction.response.send_message(f"❌ You are already in a game of Hangman in {game.message.guild.name}/{game.message.channel.name}. You can leave it using the `Leave` button under the game message.", ephemeral=True)
            return

        # Create game
        game = Game(interaction.user, expression, self.game_messages, self.users_in_games)
        if from_pack:
            game.players.append(interaction.user)

        response: PartialInteractionMessage = await interaction.response.send_message(embed=game.create_embed(), view=HangmanView(self.users_in_games))
        game.message = await response.fetch()
        
        self.users_in_games[interaction.user.id] = game
        self.game_messages[game.message.id] = game.creator.id


    @hangman.subcommand(description="Starts a game of hangman.")
    async def start(self, interaction: Interaction, expression: str):
        self.logger.info(f"{interaction.user.name} has started a game with expression {expression} in {interaction.guild.name}/{interaction.channel.name}.")

        # Remove illegal characters from expression
        legal_expression = ""
        for ch in unidecode(expression.lower()):
            if ch in ("abcdefghijklmnopqrstuvwxyz" + ALLOWED_CHARS):
                legal_expression += ch
        
        # Create game if expression is long enough
        if len(legal_expression) > 0:
            await self.start_game(interaction, legal_expression)
        else:
            await interaction.response.send_message("❌ Expression was too short or contained illegal characters.", ephemeral=True)
    
    
    @hangman.subcommand(description="Starts a game of hangman with random expression from expression pack.")
    async def start_expression_pack(self, interaction: Interaction, expression_pack: str = SlashOption(choices=PACKS.keys(), description="Theme from which a word will be picked.")):
        word = choice(PACKS[expression_pack])

        self.logger.info(f"{interaction.user.name} has started a game with expression \"{word}\" from pack {expression_pack} in {interaction.guild.name}/{interaction.channel.name}.")
        
        await self.start_game(interaction, word, True)

    
    @Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in self.game_messages.keys():
            game: Game = self.users_in_games[self.game_messages[event.message_id]]

            self.logger.info(f"Game ({event.message_id}) message in {game.message.guild.name}/{game.message.channel.name} was deleted. Removing game instance.")
            self.users_in_games[self.game_messages[event.message_id]].delete()
    

    @Cog.listener()
    async def on_raw_bulk_message_delete(self, event: RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in self.game_messages.keys():
                game: Game = self.users_in_games[self.game_messages[id]]

                self.logger.info(f"Game ({id}) message in {game.message.guild.name}/{game.message.channel.name} was deleted. Removing game instance.")
                self.users_in_games[self.game_messages[id]].delete()


def load(client: Bot):
    client.add_cog(Hangman(client))