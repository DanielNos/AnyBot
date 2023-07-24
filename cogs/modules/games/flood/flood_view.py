from nextcord.ui import View, Button
from nextcord import Interaction, Embed
from flood_board import *
from logging import Logger, getLogger
from formatting import get_place


class FloodView(View):
    def __init__(self, difficulty: bool, color_count: int, size: int, first_color: int, max_turns: int):
        super().__init__()
        self.logger: Logger = getLogger("bot")

        self.difficulty = difficulty
        self.color_count = color_count
        self.size = size
        self.turn = 1
        self.max_turns = max_turns

        for i in range(color_count):
            self.add_item(ColorButton(i, disabled=(first_color == i)))
    

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
        embed.set_field_at(0, name=f"Turn: {self.turn}/{self.max_turns}", value=board_str)

        single_color = is_single_color(board)
        
        # Victory
        if single_color:
            embed.add_field(name="🎉 You won! 🎉", value="Congratulations!", inline=False)
            embed.set_footer(text="")
            self.children = []

            self.logger.info(f"{interaction.user.name} has won a game in {get_place(interaction)}.")
        # Defeat
        elif self.difficulty != -1 and self.turn >= self.max_turns:
            embed.add_field(name="💢 You lost! 💢", value="Better luck next time!", inline=False)
            embed.set_footer(text="")
            self.children = []

            self.logger.info(f"{interaction.user.name} has lost a game of Flood in {get_place(interaction)}.")
        # Next turn
        else:
            for i in range(len(self.children)):
                self.children[i].disabled = (i == color_index)

        await interaction.response.edit_message(embed=embed, view=self)
        

class ColorButton(Button):
    def __init__(self, color_index: int, disabled: bool = False):
        super().__init__(emoji=COLOR_SQUARES[color_index], disabled=disabled)

        self.color_index = color_index


    async def callback(self, interaction: Interaction):
        await self.view.flood(interaction, self.color_index)