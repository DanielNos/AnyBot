from logging import Logger, getLogger
from nextcord.ui import View, Modal, TextInput
from nextcord import Interaction, Embed
from formatting import LETTERS_TO_EMOJIS
from polls_poll import progress_bar
from discord_emoji import to_uni


class AddOptionModal(Modal):
    def __init__(self, view: View):
        super().__init__(title="Add Option")
        self.logger: Logger = getLogger("bot")
        self.view = view

        # Add inputs
        self.option = TextInput(label="Option Text:", min_length=1, max_length=50, required=True)
        self.add_item(self.option)

        self.emoji = TextInput(label="Reaction Emoji:", min_length=1, max_length=50, required=False, placeholder="Optional. Use ':emoji:' format.")
        self.add_item(self.emoji)


    async def callback(self, interaction: Interaction):
        emoji = self.emoji.value.lower()

        # Try to extract emoji from option
        uni_emoji = to_uni(emoji)
        # Use letter if emoji couldn't be found
        if not uni_emoji:
            uni_emoji = LETTERS_TO_EMOJIS[len(self.view.poll.emojis)]
        
        self.view.poll.emojis.append(uni_emoji)

        # Add option to message
        embed: Embed = interaction.message.embeds[0]
        embed.add_field(name=uni_emoji + " " + self.option.value, value=progress_bar(), inline=False)

        # Enable completing
        self.view.children[3].disabled = False

        await interaction.response.edit_message(embed=embed, view=self.view)