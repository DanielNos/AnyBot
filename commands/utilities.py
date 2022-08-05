import sys, random
from typing import Union
from nextcord.ext import commands
from nextcord import SlashOption, slash_command, Interaction, Embed

sys.path.append("../NosBot")
import logger as log
import dataManager


LENGTH_UNITS = {
    "ym": -24,
    "zm": -21,
    "am": -18,
    "fm": -15,
    "pm": -12,
    "nm": -9,
    "μm": -6, "um": -6,
    "mm": -3,
    "cm": -2,
    "dm": -1,
    "m": 0,
    "dam": 1,
    "hm": 2,
    "km": 3,
    "M": 6,
    "G": 9,
    "T": 12,
    "P": 15,
    "E": 18,
    "Z": 21,
    "Y": 24
}


WEIGHT_UNITS = {
    "Gt": 15,
    "Mt": 12,
    "t": 6,
    "kg": 3,
    "dkg": 1,
    "g": 0,
    "mg": -3,
    "µg": -6, "ug": -6,
    "ng": -9,
    "pg": -12
}


TEST_GUILDS = []
logger = None


class Utilities(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")

    
    @commands.Cog.listener()
    async def on_ready(self):
        global TEST_GUILDS
        TEST_GUILDS = dataManager.load_test_guilds()


    @slash_command(guild_ids=TEST_GUILDS, description="Chooses between multiple choices.", force_global=True)
    async def choose(self, interaction: Interaction, choices: str):
        logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: choose " + choices + ".")

        embed: Embed = Embed(title="Picked: __" + random.choice(choices.split(" ")) + "__", color=0xFBCE9D)
        embed.add_field(name="Choices:", value=choices, inline=True)
        
        await interaction.response.send_message(embed=embed)
    

    @slash_command(guild_ids=TEST_GUILDS, description="Convert a value to a different unit.", force_global=True)
    async def convert(self, interaction: Interaction, value: str, unit: str, new_unit: str = SlashOption(description="The new unit to convert your value to.")):
        value = value.replace(",", ".")

        # Return if value isn't float
        if not is_float(value):
            await interaction.response.send_message("🚫 FAILED. Can't convert from " + unit + " to " + new_unit + " because " + value + " isn't a valid number.", ephemeral=True)
            return

        #   METRIC - METRIC CONVERSION
        metric = [LENGTH_UNITS, WEIGHT_UNITS]
        original_exponent = new_exponent =  None

        for units in metric:
            if unit in units and new_unit in units:
                original_exponent = units[unit]
                new_exponent = units[new_unit]

        # Return if can't convert between units
        if original_exponent == None or new_exponent == None:
            await interaction.response.send_message("🚫 FAILED. Can't convert from " + unit + " to " + new_unit + ".", ephemeral=True)
            return
        
        # Calculate
        result = calculate_metric(value, original_exponent, new_exponent)
        await interaction.response.send_message(value + " " + unit + " = " + result + " " + new_unit)          


def calculate_metric(value, original_exponent, new_exponent) -> float:
    number = float(value)
    difference = original_exponent - new_exponent

    result = number * 10.0 ** difference
    return format_exponent(result)


def format_exponent(value: Union[int, float]) -> str:
    value: str = str(value)

    if not "e" in value:
        return value
    
    number, exponent = value.split("e")

    return number + " * 10^" + str(int(exponent))


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except:
        return False


def load(client: commands.Bot):
    client.add_cog(Utilities(client))