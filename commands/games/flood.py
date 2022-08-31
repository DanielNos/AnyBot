import sys
from nextcord.ext import commands
from nextcord.ui import View, Button
from nextcord import ButtonStyle, Embed, SlashOption, Interaction, slash_command
from random import randint
from copy import deepcopy

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import complete_name

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

COLOR_SQUARES = ["🟥", "🟩", "🟦", "🟧", "🟨", "🟪", "🟫", "⬜"]
COLOR_CIRCLES = ["🔴", "🟢", "🔵", "🟠", "🟡", "🟣", "🟤", "⚪"]


class Controls(View):
    def __init__(self, difficulty: bool, color_count: int, size: int, first_color: int, max_turns: int):
        super().__init__()
        self.difficulty = difficulty
        self.color_count = color_count
        self.size = size
        self.turn = 1
        self.max_turns = max_turns

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
        embed.set_field_at(0, name="Turn: " + str(self.turn) + (self.difficulty != -1) * ("/" + str(self.max_turns)), value=board_str)

        single_color = is_single_color(board)
        
        # Victory
        if single_color:
            embed.add_field(name="🎉 You won! 🎉", value="Congratulations!", inline=False)
            embed.set_footer(text="")
            self.children = []
            self.add_record(interaction.user.id, True)
        # Defeat
        elif self.difficulty != -1 and self.turn >= self.max_turns:
            embed.add_field(name="💢 You lost! 💢", value="Better luck next time!", inline=False)
            embed.set_footer(text="")
            self.children = []
            self.add_record(interaction.user.id, False)
        # Next turn
        else:
            for i in range(len(self.children)):
                self.children[i].disabled = (i == color_index)

        await interaction.response.edit_message(embed=embed, view=self)
    

    def add_record(self, user_id: int, victory: bool):
        dataManager.add_game_record(user_id, "flood", victory, False)

        if not victory:
            return
        
        experience = 5 + int(self.size > 10) + int(self.size > 12) + int(self.color_count >= 5) + int(self.color_count >= 7) - int(self.difficulty == 1) - 3 * int(self.difficulty == 2)
        dataManager.add_experience_amount(user_id, experience)
        

class Flood(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
  

    @slash_command(guild_ids=TEST_GUILDS, description="Start a game of flood.", force_global=PRODUCTION)
    async def flood(self, interaction: Interaction,
    difficulty: int = SlashOption(choices={ "Hard": 0, "Medium": 1, "Easy": 2, "None": -1}),
    size: int = SlashOption(choices={"8x8": 8, "9x9": 9, "10x10": 10, "11x11": 11, "12x12": 12, "13x13": 13, "14x14": 14}, description="The size of the board."),
    colors: int = SlashOption(choices=[3, 4, 5, 6, 7, 8], description="How many colors there will be.")):
        self.logger.log_info(f"{complete_name(interaction.user)} has called command: flood difficulty={str(difficulty)} size={str(size)}x{str(size)} color_count={str(colors)}.")

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
        
        # Calculate max turn count
        diff_text = "Turn: 1"
        max_turns = 0
        if difficulty != -1:
            multiplier = 1 + int(colors >= 5) + int(colors >= 7)
            additional_turns = (int(size > 10) + int(size > 12)) * multiplier
            
            if difficulty == 1:
                additional_turns -= round(additional_turns / 2.0)
            if difficulty == 0:
                additional_turns = 0
            
            max_turns = solution_step_count(board, colors) + additional_turns
            diff_text += "/" + str(max_turns)

        # Create game embed
        embed = Embed(title="Flood")
        embed.add_field(name=diff_text, value=board_arr_to_str(board))
        embed.set_footer(text="Convert all the tiles to single color!")

        await interaction.response.send_message(embed=embed, view=Controls(difficulty, colors, size, index, max_turns), ephemeral=True)


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
    board[x][y] = "!"
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


class Node():
    def __init__(self, board, parent_node, color_count: int):
        self.board = board
        self.parent = parent_node
        self.color_count = color_count
    

    def generate_states(self):
        prev_color = COLOR_CIRCLES.index(self.board[0][0])
        
        # Create new node for every color flood option
        new_nodes = []
        for i in range(self.color_count):
            if i == prev_color:
                continue
            
            # Do the flood and create new node
            state = replace(deepcopy(self.board), self.board[0][0], COLOR_SQUARES[i])
            node = Node(replace(state, state[0][0], COLOR_CIRCLES[i]), self, self.color_count)
            new_nodes.append(node)
        
        return new_nodes

    
    def is_solved(self) -> bool:
        color = self.board[0][0]

        for y in range(len(self.board)):
            for x in range(len(self.board)):
                if color != self.board[x][y]:
                    return False
        
        return True


def solution_step_count(board, color_count: int) -> int:
    root = Node(board, None, color_count)
    queue = [root]

    while True:
        # Get the oldest node
        node = queue.pop(0)

        # If the node is solved return the number of it's parents
        if node.is_solved():
            node_count = 1

            while node.parent != None:
                node = node.parent
                node_count += 1

            return node_count
        
        # Create all possible moves
        valid_nodes = node.generate_states()
        
        # Count the new area of all moves
        color_counts = []
        for valid_node in valid_nodes:
            color_counts.append(count_color(deepcopy(valid_node.board), valid_node.board[0][0]))
        
        # Get the move with the new largest area of color
        index = color_counts.index(max(color_counts))
        # Add it to the end of the queue
        queue.append(valid_nodes[index])


def load(client: commands.Bot):
    client.add_cog(Flood(client))