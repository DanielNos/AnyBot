import sys
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, slash_command

sys.path.append("../NosBot")
import dataManager, access
import logger as log

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()
logger = None


class Clear(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="Deletes up to 100 messages from current channel.", force_global=PRODUCTION)
    async def clear(self, interaction: Interaction, amount: int = SlashOption(min_value=1, max_value=100)):
        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: clear " + str(amount) +".")
        
        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Use Clear"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to clear messages.", ephemeral=True)
            return
        
        # Remove messages
        if amount > 100: amount = 100
        if amount < 0: amount = 0

        messages = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"✅ Successfully removed {len(messages)} message" + ((len(messages)!=1)*"s") + ".", ephemeral=True)


def load(client: commands.Bot):
    client.add_cog(Clear(client))