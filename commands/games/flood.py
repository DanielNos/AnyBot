import sys
from nextcord.ext import commands
from nextcord.ui import View, Button
from nextcord import ButtonStyle, Embed, SlashOption, Interaction, slash_command
from random import randint

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import complete_name

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

COLOR_SQUARES = ["🟥", "🟩", "🟦", "🟧", "🟨", "🟪", "🟫", "⬜"]
COLOR_CIRCLES = ["🔴", "🟢", "🔵", "🟠", "🟡", "🟣", "🟤", "⚪"]


class Controls(View):
    def __init__(self, difficulty: str, color_count: int, size: int, first_color: int):
        super().__init__()
        self.difficulty = difficulty
        self.color_count = color_count
        self.size = size
        self.turn = 0

        callbacks = [self.change_color0, self.change_color1, self.change_color2, self.change_color3, self.change_color4, self.change_color5, self.change_color6, self.change_color7]
        
        for i in range(color_count):
            button: Button = Button(style=ButtonStyle.gray, emoji=COLOR_SQUARES[i], disabled=(first_color == i))
            button.callback = callbacks[i]
            self.add_item(button)
    

    async def change_color0(self, interaction: Interaction):
        await self.flood(interaction, 0)

    async def change_color1(self, interaction: Interaction):
        await self.flood(interaction, 1)

    async def change_color2(self, interaction: Interaction):
        await self.flood(interaction, 2)

    async def change_color3(self, interaction: Interaction):
        await self.flood(interaction, 3)

    async def change_color4(self, interaction: Interaction):
        await self.flood(interaction, 4)
 
    async def change_color5(self, interaction: Interaction):
        await self.flood(interaction, 5)

    async def change_color6(self, interaction: Interaction):
        await self.flood(interaction, 6)

    async def change_color7(self, interaction: Interaction):
        await self.flood(interaction, 7)
    

    async def flood(self, interaction: Interaction, color_index: int):
        board_str = interaction.message.embeds[0].fields[0].value
        board = board_str_to_arr(board_str)

        # Replace old color circles with new color squares
        board = replace(board, board[0][0], COLOR_SQUARES[color_index])
        # Replace new color squares with new color circles
        board = replace(board, board[0][0], COLOR_CIRCLES[color_index])

        # Recreate embed
        self.turn += 1
        board_str = board_arr_to_str(board)

        embed: Embed = interaction.message.embeds[0]
        embed.set_field_at(0, name="Turn: " + str(self.turn), value=board_str)

        # Check for victory
        if is_single_color(board):
            embed.add_field(name="🎉 You won! 🎉", value="Congratulations!", inline=False)
            embed.set_footer(text="")
            self.children = []
        else:
            # Disable current color button
            for i in range(len(self.children)):
                self.children[i].disabled = (i == color_index)

        await interaction.response.edit_message(embed=embed, view=self)


class Flood(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
  

    @slash_command(guild_ids=TEST_GUILDS, description="Start a game of flood.", force_global=PRODUCTION)
    async def flood(self, interaction: Interaction,
    difficulty: str = SlashOption(choices=["Easy", "Medium", "Hard", "None"]),
    size: int = SlashOption(choices={"8x8": 8, "9x9": 9, "10x10": 10, "11x11": 11, "12x12": 12, "13x13": 13, "14x14": 14}),
    colors: int = SlashOption(choices=[3, 4, 5, 6, 7, 8])):
        self.logger.log_info(f"{complete_name(interaction.user)} has called command: flood {difficulty} {str(size)}x{str(size)} {str(colors)}.")

        # Generate board
        board = []
        for y in range(size):
            row = []
            for x in range(size):
                row.append(COLOR_SQUARES[randint(0, colors-1)])
            board.append(row)
        
        index = COLOR_SQUARES.index(board[0][0])
        
        # Do the initial flood
        board = replace(board, board[0][0], COLOR_CIRCLES[index])
        
        # Create game embed
        embed = Embed(title="Flood")
        embed.add_field(name="Turn: 0", value=board_arr_to_str(board))
        embed.set_footer(text="Convert all the tiles to single color!")

        await interaction.response.send_message(embed=embed, view=Controls(difficulty, colors, size, index), ephemeral=True)


def replace(board, prev_color: str, new_color: str, x = 0, y = 0):
        board[x][y] = new_color

        # Recursively convert tile's neighbors
        if x > 0 and board[x-1][y] == prev_color:
            board = replace(board, prev_color, new_color, x-1, y)

        if y > 0 and board[x][y-1] == prev_color:
            board = replace(board, prev_color, new_color, x, y-1)
        
        if x < len(board)-1 and board[x+1][y] == prev_color:
            board = replace(board, prev_color, new_color, x+1, y)
        
        if y < len(board)-1 and board[x][y+1] == prev_color:
            board = replace(board, prev_color, new_color, x, y+1)

        return board
    

def is_single_color(board: str) -> bool:
    current_color = board[0]
    for char in board:
        if char != current_color:
            return False
    return True


def board_str_to_arr(board: str):
    board_arr = []
    row = []

    for i in range(len(board)):
        if board[i] == "\n":
            board_arr.append(row)
            row = []
        else:
            row.append(board[i])
    
    if len(row) > 0:
        board_arr.append(row)
        
    return board_arr
    

def board_arr_to_str(board):
    board_str = ""
    for row in board:
        for char in row:
            board_str += char
        board_str += "\n"
    
    return board_str


def count_color(board, color: str, x = 0, y = 0):
    count = 1
    # Recursively convert tile's neighbors
    if x > 0 and board[x-1][y] == color:
        count += count_color(board, color, x-1, y)

    if y > 0 and board[x][y-1] == color:
        count += count_color(board, color, x, y-1)

    if x < len(board)-1 and board[x+1][y] == color:
        count += count_color(board, color, x+1, y)
    
    if y < len(board)-1 and board[x][y+1] == color:
        count += count_color(board, color, x, y+1)

    return count

def solution_step_count(board, color_count: int) -> int:
    prev_color = COLOR_CIRCLES.index(board[0][0])
    board = replace(board, board[0][0], COLOR_SQUARES[prev_color])

    # Create all possible states
    states = []
    for i in range(color_count-1):
        if i == prev_color:
            continue
        
        state = replace(board, board[0][0], COLOR_SQUARES[prev_color])
        states.append(replace(state, state[0][0], COLOR_CIRCLES[i]))
    
    # Evaluate states
    color_counts = [count_color(states[0], states[0][0][0])]
    last = color_counts[0]
    same = True
    for state in states[1:]:
        count = count_color(board, board[0][0])
        if count != last:
            same = False
        last = count
        color_counts.append(count)


    best = color_counts.index(max(color_counts))
    return 1 + solution_step_count(states[best], color_count)


def load(client: commands.Bot):
    client.add_cog(Flood(client))