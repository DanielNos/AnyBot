import sys
from random import randint
from math import floor
from nextcord.ext import commands
from nextcord import slash_command, Interaction, SlashOption, Member, Embed, Message, User

sys.path.append("../../NosBot")
import dataManager
import logger as log

EMPTY_BOARD = "▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n"
TEST_GUILDS = []
INFO_DELETE_TIME = 6
WINNER_DELETE_TIME = 20

logger = None
games = {}

class Game:
    def __init__(self, player: User, opponent: User, difficulty: str = None):
        self.message: Message = None
        self.player: User = player
        self.opponent: User = opponent
        self.difficulty: str = difficulty

        self.turn: int = 1
        self.round: int = 1
        self.board = [[0,0,0], [0,0,0], [0,0,0]]
        self.board_render = self.__create_game_embed()
    

    def get_render(self):
        return self.board_render
    

    def __create_game_embed(self) -> Embed:
        embed = Embed(title="Tic-Tac-Toe | " + self.player.name + " vs. " + self.opponent.name, color=0xFBCE9D)
        embed.add_field(name="Round " + str(self.round) + " | Turn: " + ([self.player.name, self.opponent.name][self.turn-1]), value=EMPTY_BOARD)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/DanielNos/NosBot/main/icons/tictactoe.png")

        if self.difficulty != None:
            embed.add_field(name="Difficulty:", value=self.difficulty)

        embed.set_footer(text="Play using /tictactoe play [row] [column]")
        return embed
    

    def __render_board(self) -> str:
        empty = "▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️"
        line = "▫️" * 11 + "\n"
        
        # Convert values to characters
        rendered_board = []
        for y in range(3):
            row = []
            for x in range(3):
                if self.board[x][y] == 0:
                    row.append("▪️")
                elif self.board[x][y] == 1:
                    row.append("<:o2:1000763542934405181>")
                else:
                    row.append("<:negative_squared_cross_mark:1000762218159280208>")
            rendered_board.append(row)
                    
        # Assemble game board
        render = empty + "\n"
        render += "▪️" + rendered_board[0][0] + "▪️▫️▪️" + rendered_board[1][0] + "▪️▫️▪️" + rendered_board[2][0] + "▪️\n"
        render += empty + "\n" + line + empty + "\n"

        render += "▪️" + rendered_board[0][1] + "▪️▫️▪️" + rendered_board[1][1] + "▪️▫️▪️" + rendered_board[2][1] + "▪️\n"
        render += empty + "\n" + line + empty + "\n"

        render += "▪️" + rendered_board[0][2] + "▪️▫️▪️" + rendered_board[1][2] + "▪️▫️▪️" + rendered_board[2][2] + "▪️\n"
        render += empty

        return render

    
    def play(self, x, y):
        self.board[x][y] = self.turn
        
        self.turn += -int(self.turn == 2) + int(self.turn == 1)
        self.round += 1

        name = "Round " + str(floor(self.round / 2)+1) + " | Turn: " + ([self.player.name, self.opponent.name][self.turn-1])
        self.board_render.set_field_at(0, name=name, value=self.__render_board())

    
    def is_empty(self, x, y) -> bool:
        return self.board[x][y] == 0
    

    def turn_id(self) -> int:
        return [self.player.id, self.opponent.id][self.turn-1]

    
    def __get_player(self, index: int) -> User:
        return [self.player, self.opponent][index-1]
    

    def get_winner(self) -> User:
        for p in [1, 2]:
            # Check rows and columns
            for i in range(3):
                if self.board[i][0] == p and self.board[i][1] == p and self.board[i][2] == p:
                    return self.__get_player(p)
                
                if self.board[0][i] == p and self.board[1][i] == p and self.board[2][i] == p:
                    return self.__get_player(p)
            
            # Check diagonals
            if self.board[0][0] == p and self.board[1][1] == p and self.board[2][2] == p:
                return self.__get_player(p)
            
            if self.board[0][2] == p and self.board[1][1] == p and self.board[2][0] == p:
                return self.__get_player(p)
        
        return None


class TicTacToe(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")


    @commands.Cog.listener()
    async def on_ready(self):
        global TEST_GUILDS
        TEST_GUILDS = dataManager.load_test_guilds()


    @slash_command(guild_ids=TEST_GUILDS, description="Deletes up to 100 messages from current channel.", force_global=True)
    async def tictactoe(self, interaction: Interaction):
        return
    
    
    @tictactoe.subcommand(description="Concede your game of tic-tac-toe and let your opponent win.")
    async def concede(self, interaction: Interaction):
        # Return if user isn't in a game
        if not interaction.user.id in games.keys():
            await interaction.response.send_message("🚫 Failed. You can't concede because your currently aren't in a game.", ephemeral=True)
            return
        
        # Get game
        game: Game = games[interaction.user.id]
        
        # Send game end message
        winner = game.player
        loser = game.opponent
        if interaction.user.id == game.player.id:
            winner = game.opponent
            loser = game.player
            
        embed = create_victory_embed(game.board_render.title, winner)
        embed.set_footer(text=loser.name + "#" + loser.discriminator + " has conceded.")

        await interaction.response.send_message(embed=embed, delete_after=WINNER_DELETE_TIME)

        # Delete game
        games.pop(game.player.id)
        if game.difficulty == None:
            games.pop(game.opponent.id)


    @tictactoe.subcommand(description="Play a game of tic-tac-toe against me.")
    async def singleplayer(self, interaction: Interaction, difficulty: str = SlashOption(
        name="difficulty", choices=["Easy"]
    )):
        # Check if user is in a game
        if interaction.user.id in games.keys():
            await interaction.response.send_message("🚫 Failed. You are currently in a game. You can leave it using /tictactoe concede.", ephemeral=True)
            return

        # Create a new game
        game = Game(interaction.user, opponent=self.client.user, difficulty=difficulty)
        await interaction.response.send_message(embed=game.get_render())

        # Find game message
        async for message in interaction.channel.history(limit=25, oldest_first=False):
            if message.author.id != self.client.user.id or not message.embeds or not message.embeds[0].thumbnail:
                continue
        
            if message.embeds[0].thumbnail.url != "https://raw.githubusercontent.com/DanielNos/NosBot/main/icons/tictactoe.png":
                continue
            
            game.message = message
            break

        # Store game data
        games[game.player.id] = game
    

    @tictactoe.subcommand(description="Play a game of tic-tac-toe against another person.")
    async def multiplier(self, interaction: Interaction, opponent: Member):
        # Return if users are in a game
        if interaction.user.id in games.keys():
            await interaction.response.send_message("🚫 Failed. You are currently in a game. You can leave it using /tictactoe concede.", ephemeral=True)
            return
        
        if opponent.id in games.keys():
            await interaction.response.send_message("🚫 Failed. Your opponent is currently in a game.", ephemeral=True)
            return
        
        # Return if opponent is a bot
        if opponent.bot:
            await interaction.response.send_message("🚫 Failed. You can't play against a bot.", ephemeral=True)
            return

        # Create a new game
        game = Game(interaction.user, opponent)
        await interaction.response.send_message(embed=game.get_render())

        # Find game message
        async for message in interaction.channel.history(limit=20, oldest_first=False):
            if message.author.id != self.client.user.id or not message.embeds or not message.embeds[0].thumbnail:
                continue
        
            if message.embeds[0].thumbnail.url != "https://raw.githubusercontent.com/DanielNos/NosBot/main/icons/tictactoe.png":
                continue
            
            game.message = message
            break

        # Store game data
        games[game.player.id] = game
        games[game.opponent.id] = game


    @tictactoe.subcommand(description="Play your turn of tictactoe.")
    async def play(self, interaction: Interaction, 
    row: int = SlashOption(name="row", choices={ "1": 0, "2": 1, "3": 2 }),
    column: int = SlashOption(name="column", choices={ "1": 0, "2": 1, "3": 2 })
        ):
        # Return if user isn't in a game
        if not interaction.user.id in games.keys():
            await interaction.response.send_message("🚫 Failed. You currently aren't in a game. You can start one using /tictactoe [singleplayer/multiplayer].", ephemeral=True)
            return
        
        game: Game = games[interaction.user.id]

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
        if game.difficulty == None:
            return

        # Play AI players turn
        # Easy
        if game.difficulty == "Easy":
            # Pick a random space
            x = randint(0, 2)
            y = randint(0, 2)
            while game.board[x][y] != 0:
                x = randint(0, 2)
                y = randint(0, 2)
        # Medium
        elif game.difficulty == "Medium":
            pass
        # Hard
        else:
            pass
        
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


def create_victory_embed(title: str, winner: User) -> Embed:
    embed = Embed(title=title)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/DanielNos/NosBot/main/icons/tictactoe.png")
    if winner == None:
        embed.add_field(name="Result: DRAW!", value="The game has ended with a draw.", inline=False)
    else:
        embed.add_field(name="Winner: " + winner.name + "#" + winner.discriminator, value="Congratulations!", inline=False)

    return embed


def check_for_winner(game: Game):
    global games
    winner = game.get_winner()

    # Draw
    if game.round >= 10 and winner == None:
        # Update embed
        game.board_render.add_field(name="DRAW!", value="Game has ended with a draw.", inline=False)
        game.board_render.remove_footer()
        return "DRAW"

    # No winner
    if winner == None:
        return None

    # One winner
    # Update embed
    game.board_render.add_field(name="WINNER:", value=winner.mention, inline=False)
    game.board_render.remove_footer()
    
    # Delete game
    games.pop(game.player.id)
    if game.difficulty == None:
        games.pop(game.opponent.id)

    return winner


def load(client: commands.Bot):
    client.add_cog(TicTacToe(client))