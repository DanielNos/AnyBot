import sys
from nextcord.ext import commands
from nextcord import slash_command, Embed, ButtonStyle, Interaction
from nextcord import ui

sys.path.append("../NosBot")
import dataManager
import logger as log

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()
HELP = None
COMMANDS = None

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
        self.logger = log.Logger("./logs/log.txt")


    @commands.Cog.listener()
    async def on_ready(self):
        global HELP, COMMANDS

        HELP = create_help_embeds(*dataManager.load_help())
        COMMANDS = create_commands_embed(dataManager.load_commands())
    

    @slash_command(guild_ids=TEST_GUILDS, description="Show all commands and their actions. Use /help [command name] for detailed info about command.", force_global=PRODUCTION)
    async def help(self, interaction: Interaction, command: str = None):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: help.")

        # Return if help wasn't initialized
        if HELP == None:
            self.logger.log_error("Help command was called before it was initialized.")
            return
        
        # Return help
        if command == None:
            await interaction.response.send_message(embed=HELP[0], view=HelpControls())
            return
        
        # Return command info
    

    @slash_command(guild_ids=TEST_GUILDS, description="List all commands.", force_global=PRODUCTION)
    async def commands(self, interaction: Interaction):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: commands.")

        # Return if commands weren't initialized
        if COMMANDS == None: 
            self.logger.log_error("Commands command was called before it was initialized.")
            return
        
        await interaction.response.send_message(embed=COMMANDS)


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


def create_commands_embed(commands) -> Embed:
    embed: Embed = Embed(title="NosBot Commands List", color=0xFBCE9D)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/4lt3rnative/nosbot/main/nosbot.png")

    for key in commands.keys():
        values = ""

        for value in commands[key]:
            values += "``" + value + "`` "

        embed.add_field(name=key, value=values, inline=False)
    
    return embed


def create_embed_template() -> Embed:
    embed = Embed(title="NosBot Commands",  color=0xFBCE9D)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/4lt3rnative/nosbot/main/nosbot.png")
    return embed


def load(client: commands.Bot):
    client.add_cog(Help(client))