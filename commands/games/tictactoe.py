import sys
from nextcord.ext import commands
from nextcord import slash_command, PartialInteractionMessage, Interaction, SlashOption, Member, Embed, Message

sys.path.append("../../NosBot")
import dataManager
import logger as log

EMPTY_BOARD = "▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n▪️▪️▪️▫️▪️▪️▪️▫️▪️▪️▪️\n"
TEST_GUILDS = []
logger = None

games = {}
users_in_games = {}

class Game:
    def __init__(self, player_id: int, opponent_id: int = -1, difficulty: str = None):
        self.player_id = player_id
        self.opponent_id = opponent_id
        self.difficulty = difficulty

        self.turn = player_id
        self.round = 1
        self.board = [[0] * 3 ] * 3
        self.board_render = self.create_board_render()
    

    def get_render(self):
        return self.board_render
    

    def create_board_render(self) -> Embed:
        embed = Embed(title="Tic-Tac-Toe | " + str(self.player_id) + " vs. " + str(self.opponent_id))
        embed.add_field(name="Round " + str(self.round) + " | Turn: " + str(self.turn), value=EMPTY_BOARD)
        if self.difficulty != None:
            embed.add_field(name="Difficulty:", value=self.difficulty)
        embed.set_footer(text="Play using /tictactoe play [column] [row]")
        return embed


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
        await interaction.response.send_message("✅ Successfully ", ephemeral=True)
    

    @tictactoe.subcommand(description="Play a game of tic-tac-toe against me.")
    async def singleplayer(self, interaction: Interaction, difficulty: str = SlashOption(
        name="difficulty", choices=["Easy", "Medium", "Hard"]
    )):
        # Check if user is in a game
        if interaction.user.id in users_in_games.keys() or interaction.user.id in users_in_games.values():
            interaction.response.send_message("🚫 Failed. You are currently in a game. You can leave it using /tictactoe concede.", ephemeral=True)
            return

        # Create a new game
        game = Game(interaction.user.id, difficulty=difficulty)
        partial_message: PartialInteractionMessage = await interaction.response.send_message(embed=game.get_render())

        message: Message = await partial_message.fetch()

        games[message.id] = game
        users_in_games[interaction.user.id] = -1
    

    @tictactoe.subcommand(description="Play a game of tic-tac-toe against another person.")
    async def multiplier(self, interaction: Interaction, opponent: Member):
        # Check if users are in a game
        if interaction.user.id in users_in_games.keys() or interaction.user.id in users_in_games.values():
            interaction.response.send_message("🚫 Failed. You are currently in a game. You can leave it using /tictactoe concede.", ephemeral=True)
            return
        
        if opponent.id in users_in_games.keys() or opponent.id in users_in_games.values():
            interaction.response.send_message("🚫 Failed. Your opponent is currently in a game.", ephemeral=True)
            return

        # Create a new game
        game = Game(interaction.user.id, opponent_id=opponent.id)
        partial_message: PartialInteractionMessage = await interaction.response.send_message(embed=game.get_render())

        message: Message = await partial_message.fetch()

        games[message.id] = game
        users_in_games[interaction.user.id] = opponent.id
    

    @tictactoe.subcommand(description="Play your turn of tictactoe.")
    async def play(self, interaction: Interaction, 
    column: int = SlashOption(name="column", choices={ "1": 0, "2": 1, "3": 2 }),
    row: int = SlashOption(name="row", choices={ "1": 0, "2": 1, "3": 2 })
        ):
        await interaction.response.defer()


def load(client: commands.Bot):
    client.add_cog(TicTacToe(client))