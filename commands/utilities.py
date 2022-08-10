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
    "hg": 2,
    "dkg": 1, "dag": 1,
    "g": 0,
    "dg": -1,
    "cg": -2,
    "mg": -3,
    "µg": -6, "ug": -6,
    "ng": -9,
    "pg": -12
}

AREA_UNITS = {
    "km2": 6, "km²": 6,
    "ha": 4,
    "ar": 2,
    "m2": 0, "m²": 0,
    "dm2": -2, "dm²": -2,
    "cm2": -4, "cm²": -4,
    "mm2": -6, "mm²": -6
}

VOLUME_UNITS = {
    "km3": 9, "km³": 9,
    "cl": 2,
    "dl": 1,
    "m3": 0, "m³": 0,
    "dm3": -3, "dm³": -3, "l": -3,
    "cm3": -6, "cm³": -6, "ml": -6, 
    "mm3": -9, "mm³": -9
}

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()
logger = None


class Utilities(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")


    @slash_command(guild_ids=TEST_GUILDS, description="Chooses between multiple choices.", force_global=PRODUCTION)
    async def choose(self, interaction: Interaction, choices: str):
        logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: choose " + choices + ".")

        embed: Embed = Embed(title="Picked: __" + random.choice(choices.split(" ")) + "__", color=0xFBCE9D)
        embed.add_field(name="Choices:", value=choices, inline=True)
        
        await interaction.response.send_message(embed=embed)
    

    @slash_command(guild_ids=TEST_GUILDS, description="Convert a value to a different unit.", force_global=PRODUCTION)
    async def convert(self, interaction: Interaction, value: str, unit: str, new_unit: str = SlashOption(description="The new unit to convert your value to.")):
        logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: convert " + value + " " + unit + " " + new_unit + ".")
        
        # Return if value isn't float
        value = value.replace(",", ".")

        if not is_float(value):
            await interaction.response.send_message("🚫 FAILED. Can't convert from " + unit + " to " + new_unit + " because " + value + " isn't a valid number.", ephemeral=True)
            return

        # METRIC - METRIC CONVERSION
        metric = [LENGTH_UNITS, WEIGHT_UNITS, AREA_UNITS, VOLUME_UNITS]

        for units in metric:
            if unit in units and new_unit in units:
                result = calculate_metric(value, units[unit], units[new_unit])
                await interaction.response.send_message(value + " " + unit + " = " + result + " " + new_unit)
                return
        
        # TEMPERATURE CONVERSION
        value = float(value)
        if unit.lower() == "°k":
            unit = "K"
        if new_unit.lower() == "°k":
            new_unit = "K"

        result = convert_temperature(value, unit.lower(), new_unit.lower())
        if result != None:
            await interaction.response.send_message(str(value) + " " + unit + " = " + result + " " + new_unit)
            return

        # Can't convert between units
        await interaction.response.send_message("🚫 FAILED. Can't convert from " + unit + " to " + new_unit + ".", ephemeral=True)  


def calculate_metric(value: str, original_exponent: int, new_exponent: int) -> float:
    number = float(value)
    difference = original_exponent - new_exponent

    result = number * 10.0 ** difference
    return format_exponent(result)


def convert_temperature(value: float, original_unit: str, new_unit: str) -> str:
        # Fahrenheit to Celsius
        if original_unit == "°f" and new_unit == "°c":
            return str((value - 32.0) / 1.8)
        
        # Celsius to Fahrenheit
        if original_unit == "°c" and new_unit == "°f":
            return str((value * 1.8) + 32.0)
        
        # Celsius to Kelvin
        if original_unit == "°c" and new_unit == "k":
            return str(value + 273.15)
        
        # Kelvin to Celsius
        if original_unit == "k" and new_unit == "°c":
            return str(value - 273.15)
        
        # Fahrenheit to Kelvin
        if original_unit == "°f" and new_unit == "k":
            return str(((value - 32) / 1.8) + 273.15)
        
        # Kelvin to Fahrenheit
        if original_unit == "k" and new_unit == "°f":
            return str(((value - 273.15) * 1.8) + 32)

        return None


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