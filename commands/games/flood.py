import sys
from nextcord.ext import commands
from nextcord.ui import View, Button
from nextcord import ButtonStyle, Embed, SlashOption, Interaction, slash_command
from random import randint

sys.path.append("../NosBot")
import logger as log
import dataManager

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

COLOR_SQUARES = ["🟥", "🟨", "🟩", "🟧", "🟦", "🟪", "🟫", "⬜"]
COLOR_CIRCLES = ["🔴", "🟡", "🟢", "🟠", "🔵", "🟣", "🟤", "⚪"]


class Controls(View):
    def __init__(self, logger: log.Logger, color_count: int, size: int):
        super().__init__()
        self.color_count = color_count
        self.size = size

        callbacks = [self.change_color0, self.change_color1, self.change_color2, self.change_color3, self.change_color4, self.change_color5, self.change_color6, self.change_color7]
        
        for i in range(color_count):
            button: Button = Button(style=ButtonStyle.gray, emoji=COLOR_SQUARES[i])
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

    
    def board_str_to_arr(self, board: str):
        board_arr = []
        row = []

        for i in range(len(board)):
            if board[i] == "\n":
                board_arr.append(row)
                row = []
            else:
                row.append(board[i])
            
        return board_arr
    

    def board_arr_to_str(self, board):
        board_str = ""
        for y in range(len(board)):
            for x in range(len(board[0])):
                board_str += board[y][x]
            board += "\n"
            
        return board_str
    

    async def flood(self, interaction: Interaction, color_index: int):
        board_str = interaction.message.embeds[0].fields[0].value
        board = self.board_str_to_arr(board_str)

        prev_color = COLOR_CIRCLES.index(board[0][0])
        new_color = color_index

        board = self.replace(board, COLOR_CIRCLES[prev_color], COLOR_SQUARES[new_color])

        embed: Embed = interaction.message.embeds[0]
        embed.fields[0].value = self.board_arr_to_str(board)
        await interaction.response.edit_message(embed=embed)
    

    def replace(self, board, prev_color: str, new_color: str, x = 0, y = 0):
        board[x][y] = new_color

        if x > 0 and board[x-1][y] == prev_color:
            board = self.replace(board, prev_color, new_color, x-1, y)

        if y > 0 and board[x][y-1] == prev_color:
            board = self.replace(board, prev_color, new_color, x, y-1)
        
        if x < self.size-1 and board[x+1][y] == prev_color:
            board = self.replace(board, prev_color, new_color, x+1, y)
        
        if y < self.size-1 and board[x][y+1] == prev_color:
            board = self.replace(board, prev_color, new_color, x, y+1)

        return board
        


class Flood(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
  

    @slash_command(guild_ids=TEST_GUILDS, description="Start a game of flood.", force_global=PRODUCTION)
    async def flood(self, interaction: Interaction, colors: int = SlashOption(choices=[3, 4, 5, 6, 7])):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: flood.")

        board = ""
        for i in range((10 * 10) - 1):
            if len(board) % 11 == 0:
                board += "\n"
            board += COLOR_SQUARES[randint(0, colors)]
        
        board += COLOR_CIRCLES[randint(0, colors)]
        
        embed = Embed(title="Turn: 0")
        embed.add_field(name="Board:", value=board[::-1])

        await interaction.response.send_message(embed=embed, view=Controls(self.logger, colors, 10), ephemeral=True)


def load(client: commands.Bot):
    client.add_cog(Flood(client))

