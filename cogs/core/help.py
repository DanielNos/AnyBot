import logging, os
from logging import Logger
from nextcord import Interaction, Button, ButtonStyle, Embed, slash_command
from nextcord.ext.commands import Cog, Bot
from nextcord.ui import View, button
import config


def load_help():
    pages = []

    # Search for .help files
    for dirpath, dirnames, filenames in os.walk("./cogs/modules/"):
        for filename in filenames:
            if filename.endswith(".help"):
                # Load file
                path = os.path.join(dirpath, filename)

                file = open(path, "r", encoding="utf-8")
                lines = file.readlines()
                file.close()
                
                # Invalid formatting
                if len(lines) % 2 != 0:
                    continue
                
                # Create embed with commands
                embed = Embed(title=f"NosBot Help - {filename[:-5]}", color=config.BOT["color"])
                
                for i in range(0, len(lines), 2):
                    embed.add_field(name=lines[i], value=lines[i+1])

                pages.append(embed)

    return pages


class HelpView(View):
    def __init__(self, logger: Logger, pages):
        super().__init__(timeout=None)
        self.logger = logger

        self.page = 0
        self.pages = pages

        self.button_previous: Button = self.children[0]
        self.button_page: Button = self.children[1]
        self.button_next: Button = self.children[2]

        # Set pages indicator
        self.button_page.label = f"1/{len(self.pages)}"
        if len(self.pages) == 1:
            self.button_next.disabled = True


    @button(label="Previous", style=ButtonStyle.blurple, disabled=True)
    async def previous(self, button: Button, interaction: Interaction):

        await interaction.response.defer()

        if self.page <= 0:
            return
            
        self.page -= 1

        if self.page == 0:
            button.disabled = True

        self.button_next.disabled = False
        self.button_page.label = f"{self.page + 1}/{len(self.pages)}"

        await interaction.edit_original_message(embed=self.pages[self.page], view=self)


    @button(label="1/1", style=ButtonStyle.gray)
    async def page_button(self, button: Button, interaction: Interaction):
        await interaction.response.defer()


    @button(label="Next", style=ButtonStyle.blurple)
    async def next(self, button: Button, interaction: Interaction):

        await interaction.response.defer()

        if self.page >= len(self.pages) - 1:
            return
        
        self.page += 1

        if self.page == len(self.pages) - 1:
            button.disabled = True

        self.button_previous.disabled = False
        self.button_page.label = f"{self.page + 1}/{len(self.pages)}"

        await interaction.edit_original_message(embed=self.pages[self.page], view=self)


class Help(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")

        self.help_embeds = load_help()
    

    @slash_command(name="help", description="Shows information about all commands.", guild_ids=config.DEBUG["test_guilds"])
    async def help(self, interaction: Interaction):
        await interaction.response.send_message(embed=self.help_embeds[0], view=HelpView(self.logger, self.help_embeds))


def load(client):
    client.add_cog(Help(client))