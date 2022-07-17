import sys
from nextcord.ext import commands
from nextcord import slash_command, Embed, ButtonStyle, Interaction
from nextcord import ui

sys.path.append("../NosBot")
import dataManager
import logger as log

TEST_GUILDS = []
HELP = None
logger = None


class HelpControls(ui.View):
    def __init__(self):
        super().__init__()
        self.page = 0
    

    @ui.button(label="Previous", style=ButtonStyle.gray)
    async def previous(self, button: ui.Button, interaction: Interaction):
        # Change page
        if self.page > 0:
            self.page -= 1
        else:
            await interaction.response.defer()
            return

        # Update embed
        await interaction.message.edit(embed=HELP[self.page])
        await interaction.response.defer()


    @ui.button(label="Next", style=ButtonStyle.gray)
    async def next(self, button: ui.Button, interaction: Interaction):
        # Change page
        if self.page < len(HELP)-1:
            self.page += 1
        else:
            await interaction.response.defer()
            return

        # Update embed
        await interaction.message.edit(embed=HELP[self.page])
        await interaction.response.defer()


class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("../logs/log.txt")


    @commands.Cog.listener()
    async def on_ready(self):
        global HELP, TEST_GUILDS

        TEST_GUILDS = dataManager.load_test_guilds()
        HELP = create_help_embeds(*dataManager.load_help())
    

    @slash_command(guild_ids=TEST_GUILDS, description="Show all commands and their actions. Use /help [command name] for detailed info about command.", force_global=True)
    async def help(self, interaction: Interaction):

        logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: help.")
        # Return if help wasn't initialized
        if HELP == None: 
            logger.log_error("Help command was called before it was initialized.")
            return

        await interaction.response.send_message(embed=HELP[0], view=HelpControls())


def create_help_embeds(commands, actions):
    cpr = dataManager.load_config()["commands_per_page"]

    embeds = []
    embed = create_embed_template()

    # Create embeds and populate them
    for i in range(1, len(commands)+1):
        embed.add_field(name=commands[i-1], value=actions[i-1], inline=False)
        if i % cpr == 0:
            embeds.append(embed)
            embed = create_embed_template()

    if len(embed.fields) > 0:
        embeds.append(embed)
    
    # Add page numbers
    embed_count = len(embeds)
    for i in range(embed_count):
        embeds[i].set_footer(text=("Page: " + str(i+1) + "/" + str(embed_count)))

    return embeds


def create_embed_template() -> Embed:
    embed = Embed(title="NosBot Commands",  color=0xFBCE9D)
    embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/990276313287888896/f4fa1fc1207e7430a510ed6b367da042.png?size=256")
    return embed


def load(client: commands.Bot):
    client.add_cog(Help(client))