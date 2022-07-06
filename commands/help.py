import nextcord, sys
from nextcord.ext import commands
from nextcord import Interaction, slash_command, Embed
sys.path.append("../NosBot")
import dataManager

TEST_GUILD = 794290505273966604
HELP: Embed = None

class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        global HELP

        embed: Embed = Embed(title="NosBot Commands", color=0xFBCE9D)

        help = dataManager.load_help()

        embed.add_field(name="Command", value=help[0], inline=True)
        embed.add_field(name="Action", value=help[1], inline=True)

        HELP = embed
    

    @slash_command(guild_ids=[TEST_GUILD], description="Show all commands and their actions.")
    async def help(self, interaction: Interaction):
        await interaction.response.send_message(embed=HELP)


def load(client: commands.Bot):
    client.add_cog(Help(client))