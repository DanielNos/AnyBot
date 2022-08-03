import sys, random
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
        
        # Length M-M
        if unit in LENGTH_UNITS and new_unit in LENGTH_UNITS:
            # Return if value isn't float
            if not is_float(value):
                await interaction.response.send_message("🚫 FAILED. Can't convert from " + unit + " to " + new_unit + " because " + value + " isn't a valid number.", ephemeral=True)
                return

            # Calculate
            number = float(value)
            factor = LENGTH_UNITS[unit] - LENGTH_UNITS[new_unit]

            result = number * 10.0 ** factor
            result = format_exponent(result)

            await interaction.response.send_message(value + " " + unit + " = " + result + " " + new_unit)
            return

        await interaction.response.send_message("🚫 FAILED. Can't convert from " + unit + " to " + new_unit + ".", ephemeral=True)


def format_exponent(value: float | int) -> str:
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