import sys, nextcord
from nextcord.ui import View, Button
from nextcord.ext import commands
from nextcord import ButtonStyle, Embed, Interaction, slash_command
from random import randint

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import complete_name

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

COLORS = ["🟥", "🟩", "🟦", "🟧", "🟨", "🟪"]


class Controls(View):
    def __init__(self):
        super().__init__()
        self.turn = 0
        self.combinations = [[],[],[],[],[],[],[],[],[],[]]
        self.correct = []

        # Create correct combination
        colors = COLORS.copy()
        for i in range(4):
            self.correct.append(colors.pop(randint(0, 5 - i)))
        print(self.correct)

        # Add buttons
        callbacks = [self.pick_color0, self.pick_color1, self.pick_color2, self.pick_color3, self.pick_color4, self.pick_color5]

        for i in range(3):
            button: Button = Button(style=ButtonStyle.gray, label=COLORS[i], row=0)
            button.callback = callbacks[i]
            self.add_item(button)
        
        for i in range(3, 6):
            button: Button = Button(style=ButtonStyle.gray, label=COLORS[i], row=1)
            button.callback = callbacks[i]
            self.add_item(button)
        
        button: Button = Button(style=ButtonStyle.green, label="Submit", row=2, disabled=True)
        button.callback = self.submit
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.red, label="Clear", row=2)
        button.callback = self.clear
        self.add_item(button)
    
    
    async def pick_color0(self, interaction: Interaction):
        await self.pick_color(interaction, 0)
    
    async def pick_color1(self, interaction: Interaction):
        await self.pick_color(interaction, 1)
    
    async def pick_color2(self, interaction: Interaction):
        await self.pick_color(interaction, 2)
    
    async def pick_color3(self, interaction: Interaction):
        await self.pick_color(interaction, 3)
    
    async def pick_color4(self, interaction: Interaction):
        await self.pick_color(interaction, 4)

    async def pick_color5(self, interaction: Interaction):
        await self.pick_color(interaction, 5)

    
    def set_buttons(self, enabled: bool):
        enabled = not enabled
        for i in range(6):
            self.children[i].disabled = enabled
        self.children[6].disabled = not enabled

    
    async def pick_color(self, interaction: Interaction, index: int):
        if len(self.combinations[self.turn]) < 4:
            self.combinations[self.turn].append(COLORS[index])

        if len(self.combinations[self.turn]) == 4:
            self.set_buttons(enabled=False)

        await interaction.response.edit_message(embed=create_board(self.combinations, self.turn, self.correct), view=self)

    
    async def clear(self, interaction: Interaction):
        self.combinations[self.turn] = []

        self.set_buttons(enabled=True)
        
        await interaction.response.edit_message(embed=create_board(self.combinations, self.turn, self.correct), view=self)

    
    async def submit(self, interaction: Interaction):
        self.set_buttons(enabled=True)
        self.turn += 1

        embed: Embed = create_board(self.combinations, self.turn, self.correct)

        # Remove controls if game is over
        if self.turn >= 10 or self.combinations[self.turn-1] == self.correct:
            self.children = []

            if self.combinations[self.turn-1] == self.correct:
                embed.add_field(name="🎉 You won! 🎉", value="Congratulations!", inline=False)
                dataManager.add_game_record(interaction.user.id, "mastermind", True)
            else:
                embed.add_field(name="💢 You lost! 💢", value="Better luck next time!", inline=False)
                dataManager.add_game_record(interaction.user.id, "mastermind", False)

        await interaction.response.edit_message(embed=embed, view=self)
    

class Mastermind(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="Start a game of mastermind.", force_global=PRODUCTION)
    async def mastermind(self, interaction: Interaction):
        self.logger.log_info(complete_name(interaction.user) + " has called command: mastermind.")

        await interaction.response.send_message(embed=create_board(), view=Controls(), ephemeral=True)


def create_board(combinations = None, turn = 0, correct = None):
    embed: Embed = Embed(title="Mastermind")
    
    offset = 0
    if combinations and correct and turn > 0 and combinations[turn-1] == correct:
      offset = -1

    text = "```"
    for i in range(0, 10):
        # Create index
        index = str(i+1)
        if i+1 < 10:
            index = " " + index
        index = "  " + index

        # Create combination
        combination = ""
        if not combinations:
            # Empty combination
            combination = "🔳 🔳 🔳 🔳 "
        else:
            # Get combination
            for j in range(4):
                if j < len(combinations[i]):
                    combination += combinations[i][j] + " "
                else:
                    combination += "🔳 "
            combination = combination[:-1]

        # Create hints
        color = 0
        col_pos = 0

        if i < turn and correct is not None:
            for j in range(4):
                if combinations[i][j] == correct[j]:
                    col_pos +=1
                elif combinations[i][j] in correct:
                    color += 1

        # Assemble row
        if i == turn + offset:
            text += "▶️ " + index[2:] + " " + combination + " " + str(color) +" | " + str(col_pos) +" ◀️\n"
        else:
            text += index + " " + combination + " " + str(color) +" | " + str(col_pos) +"\n"

    if turn >= 9:
        turn = 9
        
    if not combinations or not correct or turn > 0 and turn < 9 and combinations[turn-1] != correct:
        embed.set_footer(text="Figure out the correct combination!")

    embed.add_field(name="Turn: " + str(turn+1) + "/10", value=text + "```")
    return embed


def load(client: commands.Bot):
    client.add_cog(Mastermind(client))