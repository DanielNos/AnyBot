import os, sys
sys.path.append(os.path.dirname(__file__))

from config import DEBUG
from logging import Logger, getLogger
from random import randint
from nextcord.ext import commands
from nextcord import slash_command, PartialInteractionMessage, Interaction, SlashOption, Member, Embed, Message, User, RawMessageDeleteEvent, RawBulkMessageDeleteEvent
from tictactoe_game import Game


INFO_DELETE_TIME = 6
WINNER_DELETE_TIME = 20


class TicTacToe(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger: Logger = getLogger("bot")

        self.games = {}
        self.game_messages = {}


    @slash_command(guild_ids=DEBUG["test_guilds"])
    async def tictactoe(self, interaction: Interaction):
        return
    
    
    @tictactoe.subcommand(description="Concede your game of tic-tac-toe and let your opponent win.")
    async def concede(self, interaction: Interaction):

        # Return if user isn't in a game
        if not interaction.user.id in self.games.keys():
            await interaction.response.send_message("🚫 Failed. You can't concede because your currently aren't in a game.", ephemeral=True)
            return
        
        # Get game
        game: Game = self.games[interaction.user.id]
        
        # Send game end message
        winner = game.player
        loser = game.opponent
        if interaction.user.id == game.player.id:
            winner = game.opponent
            loser = game.player
            
        embed = create_victory_embed(game.board_render.title, winner)
        embed.set_footer(text=loser.name + "#" + loser.discriminator + " has conceded.")

        await interaction.response.send_message(embed=embed, delete_after=WINNER_DELETE_TIME)
        self.logger.info(f"{interaction.user.name} conceded their game of Tic-Tac-Toe ({game.message.id} in {game.message.guild.name}/{game.message.channel.name}.")

        # Delete game
        game.delete()


    @tictactoe.subcommand(description="Start a game of Tic-Tac-Toe.")
    async def start(self, interaction: Interaction,
                    type: str = SlashOption(name="type", choices=["Singleplayer", "Multiplayer"]),
                    opponent: Member = None
                    ):
        self.logger.info(f"{interaction.user.name} has started a {type} game of Tic-Tac-Toe in {interaction.guild.name}/{interaction.channel.name}.")

        singleplayer = (type == "Singleplayer")

        # Check if user is in a game
        if interaction.user.id in self.games.keys():
            await interaction.response.send_message("🚫 Failed. You are currently in a game. You can leave it using /tictactoe concede.", ephemeral=True)
            return
        
        # Check if parameters are set correctly
        if not singleplayer and opponent is None:
            await interaction.response.send_message("🚫 Failed. You tried to start a multiplayer game but didn't specify opponent.", ephemeral=True)
            return
        
        if opponent is not None:
            # Return if opponent is a bot
            if opponent.bot:
                await interaction.response.send_message("🚫 Failed. You can't play against a bot.", ephemeral=True)
                return
        
            # Check if opponent is in a game
            if opponent.id in self.games.keys():
                await interaction.response.send_message("🚫 Failed. Your opponent is currently in a game.", ephemeral=True)
                return
        
        else:
            opponent = self.client.user

        # Create a new game
        game = Game(interaction.user, opponent)

        message: PartialInteractionMessage = await interaction.response.send_message(embed=game.get_render())
        game.message = await message.fetch()    

        # Store game data
        self.games[game.player.id] = game
        self.game_messages[game.message.id] = game.player.id

        if opponent is not None:
            self.games[game.opponent.id] = game


    @tictactoe.subcommand(description="Play your turn of tictactoe.")
    async def play(self, interaction: Interaction, 
    row: int = SlashOption(name="row", choices={ "1": 0, "2": 1, "3": 2 }),
    column: int = SlashOption(name="column", choices={ "1": 0, "2": 1, "3": 2 })
        ):

        # Return if user isn't in a game
        if not interaction.user.id in self.games.keys():
            await interaction.response.send_message("🚫 Failed. You currently aren't in a game. You can start one using /tictactoe [singleplayer/multiplayer].", ephemeral=True)
            return
        
        game: Game = self.games[interaction.user.id]

        # Return if it isn't users turn
        if game.turn_id() != interaction.user.id:
            await interaction.response.send_message("🚫 Failed. It's not your turn now.", ephemeral=True)
            return
        
        # Return if slot is occupied
        if not game.is_empty(row, column):
            await interaction.response.send_message("🚫 Failed. The slot you selected is not empty.", ephemeral=True)
            return
        
        # Play players turn
        game.play(row, column)
        await game.message.edit(embed=game.board_render)
        
        self.logger.info(f"{interaction.user.name} has played a turn of Tic-Tac-Toe ({game.message.id}): row={row}, column={column}.")

        # Check for winner
        winner = check_for_winner(game)
        if winner != None:
            await game.message.edit(embed=game.board_render)
            if winner == "DRAW":
                winner = None
            await interaction.response.send_message(embed=create_victory_embed(game.board_render.title, winner), delete_after=WINNER_DELETE_TIME)
            return

        # Notify about play
        await interaction.response.send_message(content="ℹ️ " + interaction.user.name + " has played their turn.", delete_after=INFO_DELETE_TIME)  

        # Return if game is multiplayer
        if game.opponent != self.client.user:
            return

        # Play AI players turn
        # Pick a random space
        x = randint(0, 2)
        y = randint(0, 2)
        while game.board[x][y] != 0:
            x = randint(0, 2)
            y = randint(0, 2)
        
        game.play(x, y)
        await game.message.edit(embed=game.board_render)
        
        # Check for winner again
        winner = check_for_winner(game)
        if winner != None:
            await game.message.edit(embed=game.board_render)
            if winner == "DRAW":
                winner = None
            await interaction.response.send_message(embed=create_victory_embed(game.board_render.title, winner), delete_after=WINNER_DELETE_TIME)
            return

    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in self.game_messages.keys():
            self.logger.info(f"Tic-Tac-Toe ({event.message_id}) message was deleted. Removing game instance.")

            player_id = self.game_messages.pop(event.message_id)
            game: Game = self.games[player_id]

            self.games.pop(game.player.id)
            if game.difficulty is None:
                self.games.pop(game.opponent.id)
    

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, event: RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in self.game_messages.keys():
                self.logger.info(f"Tic-Tac-Toe ({id}) message was deleted. Removing game instance.")

                player_id = self.game_messages.pop(id)
                game: Game = self.games[player_id]

                self.games.pop(game.player.id)
                if game.difficulty is None:
                    self.games.pop(game.opponent.id)


def create_victory_embed(title: str, winner: User) -> Embed:
    embed = Embed(title=title)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/4lt3rnative/nosbot/main/tictactoe.png")
    if winner is None:
        embed.add_field(name="Result: DRAW!", value="The game has ended with a draw.", inline=False)
    else:
        embed.add_field(name="Winner: " + winner.name + "#" + winner.discriminator, value="Congratulations!", inline=False)

    return embed


def check_for_winner(game: Game):
    winner = game.get_winner()

    # DRAW
    if game.round >= 10 and winner is None:
        # Update embed
        game.board_render.add_field(name="DRAW!", value="Game has ended with a draw.", inline=False)
        game.board_render.remove_footer()

        game.delete()
        return "DRAW"

    # NO WINNER
    if winner is None:
        return None

    # ONE WINNER
    # Update embed
    game.board_render.add_field(name="WINNER:", value=winner.mention, inline=False)
    game.board_render.remove_footer()
    
    # Delete game
    game.delete()    

    return winner


def load(client: commands.Bot):
    client.add_cog(TicTacToe(client))