from nextcord.interactions import Interaction
from nextcord.ui import View, Button
from nextcord import ButtonStyle, Interaction, Embed
from random import randint
from mastermind_board import create_board


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

        # Add buttons
        for i in range(6):
            self.add_item(ColorButton(i, self))
        
        button: Button = Button(style=ButtonStyle.green, label="Submit", row=2, disabled=True)
        button.callback = self.submit
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.red, label="Clear", row=2)
        button.callback = self.clear
        self.add_item(button)

    
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
            else:
                embed.add_field(name="💢 You lost! 💢", value="Better luck next time!", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)


class ColorButton(Button):
    def __init__(self, color_index, controls: Controls):
        super().__init__(label=COLORS[color_index], row=int(color_index > 2))
        
        self.color_index = color_index
        self.controls = controls


    async def callback(self, interaction: Interaction):
        await self.controls.pick_color(interaction, self.color_index)