import sys, re
from typing import Optional, Union
from nextcord.ext import commands
from nextcord import slash_command, Interaction, ButtonStyle, Embed, Emoji, PartialEmoji
from nextcord.ui import View, Button

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import complete_name

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()


class CustomButton(Button):
    def __init__(self, *, style: ButtonStyle = ..., label: Optional[str] = None, disabled: bool = False, custom_id: Optional[str] = None, url: Optional[str] = None, emoji: Optional[Union[str, Emoji, PartialEmoji]] = None, row: Optional[int] = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
    
    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        await process_button(interaction, self.label)


class Controls(View):
    def __init__(self):
        super().__init__()

        page = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["0", "00", "."]
        ]

        controls = [ 
            ["⨯", "Exit"],
            ["÷", "⌫"],
            ["+", "Clear"],
            ["-", "="]
        ]

        # Add buttons
        for y in range(4):
            for x in range(3):
                button: CustomButton = CustomButton(label=page[y][x], style=ButtonStyle.gray, row=y)
                self.add_item(button)
            
            button: CustomButton = CustomButton(label=controls[y][0], style=ButtonStyle.blurple, row=y)
            self.add_item(button)
            
            style = ButtonStyle.red
            if y == 3:
                style = ButtonStyle.green
            button: CustomButton = CustomButton(label=controls[y][1], style=style, row=y)
            self.add_item(button)


async def process_button(interaction: Interaction, button: str):
    expression = interaction.message.embeds[0].fields[0].value.strip("`")
    
    # Get last number
    last_num = ""
    for char in expression[::-1]:
        if char not in "⨯÷+-":
            last_num += char
        else:
            break
    
    last_num = last_num[::-1]
    error = False

    # PROCESS BUTTON
    if button == "Exit":
        await interaction.channel.delete_messages(messages=[interaction.message])
        return

    # Numbers
    elif button in "0123456789" or button == "00":
        if last_num == "0":
            if button == "00":
                button = "0"
            expression = expression[:-1]
        expression += button
    
    # Operations
    elif button in "⨯÷+-":
        if expression[-1:] not in "0123456789":
            return
        expression += button
    
    # Delete and clear
    elif button == "⌫":
        if len(expression) > 1:
            expression = expression[:-1]
        else:
            expression = "0"

    elif button == "Clear":
        expression = "0"
    
    # Calculate
    elif button == "=":
        # Check for incomplete decimals
        for number in re.split("⨯÷+-", expression):
            if number.endswith("."):
                expression = "0"
                error = True
                break
        
        # Replace symbols
        expression = expression.replace("⨯", "*")
        expression = expression.replace("÷", "/")

        expression = str(eval(expression))
    
    # Dot
    elif button == ".":
        if "." not in last_num:
            expression += "."
    
    # CREATE EMBED
    embed: Embed = Embed(title="Calculator", color=0xFBCE9D)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/4lt3rnative/nosbot/main/calculator.png")
    embed.add_field(name="⠀" * int(not error) + "Error!" * int(error), value="```" + expression + "```")

    await interaction.message.edit(embed=embed)


class Calculator(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="Open calculator.", force_global=PRODUCTION)
    async def calculator(self, interaction: Interaction):
        self.logger.log_info(complete_name(interaction.user) + " has called command: calculator.")

        embed: Embed = Embed(title="Calculator", color=0xFBCE9D)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/4lt3rnative/nosbot/main/calculator.png")
        embed.add_field(name="⠀", value="```0```")

        await interaction.response.send_message(embed=embed, view=Controls(), ephemeral=True)


def load(client: commands.Bot):
    client.add_cog(Calculator(client))