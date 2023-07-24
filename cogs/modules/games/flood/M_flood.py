import os, sys
sys.path.append(os.path.dirname(__file__))

from logging import Logger, getLogger
from nextcord.ext import commands
from nextcord import Embed, SlashOption, Interaction, slash_command
from random import randint
import config
from flood_view import FloodView
from flood_board import *
from formatting import get_place


class Flood(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger: Logger = getLogger("bot")
  

    @slash_command(guild_ids=config.DEBUG["test_guilds"], description="Start a game of flood.")
    async def flood(self, interaction: Interaction,
    difficulty: int = SlashOption(choices={ "Hard": 0, "Medium": 1, "Easy": 2, "None": -1}),
    size: int = SlashOption(choices={"8x8": 8, "9x9": 9, "10x10": 10, "11x11": 11, "12x12": 12, "13x13": 13, "14x14": 14}, description="The size of the board."),
    colors: int = SlashOption(choices=[3, 4, 5, 6, 7, 8], description="How many colors there will be.")):
        
        self.logger.info(f"{(interaction.user.name)} has started a game difficulty={str(difficulty)} size={str(size)}x{str(size)} color_count={str(colors)} in {get_place(interaction)}.")

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

            if difficulty == 1 and multiplier > 1:
                multiplier -= 1
            if difficulty == 0:
                multiplier = 0

            additional_turns = (1 + (int(size > 10) + int(size > 12))) * multiplier

            max_turns = solution_step_count(board, colors) + additional_turns
            diff_text += "/" + str(max_turns)

        # Create game embed
        embed = Embed(title="Flood")
        embed.add_field(name=diff_text, value=board_arr_to_str(board))
        embed.set_footer(text="Convert all the tiles to single color!")

        await interaction.response.send_message(embed=embed, view=FloodView(difficulty, colors, size, index, max_turns), ephemeral=True)


def load(client: commands.Bot):
    client.add_cog(Flood(client))