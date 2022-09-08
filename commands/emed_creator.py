import sys
from nextcord.ext import commands
from nextcord import slash_command, Interaction, ButtonStyle, Embed, TextInputStyle, Colour
from nextcord.ui import Modal, View, Button, TextInput

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import complete_name

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()


class SetValueModal(Modal):
    def __init__(self, target: str):
        # Create modal title
        title = "Set " + target

        if target in ["add field", "edit field", "remove field"]:
            title = target.capitalize()

        super().__init__(title=title)
        self.target = target

        label = target.capitalize() + ":"
        
        # Add inputs
        if target in ["title", "description"]:
            self.text = TextInput(label=label, style=TextInputStyle.paragraph, required=False, max_length=256 * int(target == "title") + 4096 * int(target == 4096))
            self.add_item(self.text)
        
        if target in ["image", "thumbnail"]:
            self.url = TextInput(label=label, style=TextInputStyle.paragraph, placeholder=("Enter " + target + " URL"))
            self.add_item(self.url)
        
        if target == "color":
            self.info = TextInput(label="Info:", default_value="Enter a color using its hex code or its RGB components.", max_length=0, required=False)
            self.color = TextInput(label="Hex Code:", style=TextInputStyle.short, placeholder="aabbcc", required=False, min_length=6, max_length=6)
            self.r = TextInput(label="Red:", style=TextInputStyle.short, placeholder="0 - 255", required=False, max_length=3)
            self.g = TextInput(label="Green:", style=TextInputStyle.short, placeholder="0 - 255", required=False, max_length=3)
            self.b = TextInput(label="Blue:", style=TextInputStyle.short, placeholder="0 - 255", required=False, max_length=3)

            for item in [self.info, self.color, self.r, self.g, self.b]:
                self.add_item(item)

        if target in ["add field", "edit field"]:
            if target == "edit field":
                self.index = TextInput(label="Field Index:", style=TextInputStyle.short, required=True, max_length=2, placeholder="1")
                self.add_item(self.index)

            self.name = TextInput(label="Name:", style=TextInputStyle.paragraph, required=False, max_length=256)
            self.value = TextInput(label="Value:", style=TextInputStyle.paragraph, required=False, max_length=1024)
            self.inline = TextInput(label="Inline:", style=TextInputStyle.short, required=True, max_length=3, default_value="No", placeholder="Yes/No")
            
            for item in [self.name, self.value, self.inline]:
                self.add_item(item)
        
        if target == "remove field":
            self.index = TextInput(label="Field Index:", style=TextInputStyle.short, required=True, max_length=2, placeholder="1")
            self.add_item(self.index)

        if target in ["footer", "author"]:
            self.text = TextInput(label="Text:", style=TextInputStyle.paragraph, required=False, max_length=2048 * int(target == "footer") + 256 * int(target == "author"))
            self.add_item(self.text)


    async def callback(self, interaction: Interaction):
        original_embed: Embed = interaction.message.embeds[0]
        await interaction.response.defer()

        # Get original values
        title = original_embed.title
        description = original_embed.description
        color = original_embed.color

        # Get and format text
        if self.target not in ["add field", "edit field", "remove field", "color", "image", "thumbnail"]:
            text = self.text.value
            if len(text) == 0 and self.target == "title":
                text = "⠀"
            
        if self.target in ["add field", "edit field"]:
            field_name = self.name.value.strip()
            field_value = self.value.value.strip()

            if len(field_name) == 0:
                field_name = "⠀"
            if len(field_value) == 0:
                field_value = "⠀"

        # Edit correct value
        if self.target == "title":
            title = text
        if self.target == "description":
            description = text
        if self.target == "color":
            color = Embed.Empty
            # Get color from hex
            if len(self.color.value) == 6:
                # Check if it is valid hex code
                valid = True
                for char in self.color.value.lower():
                    if char not in "0123456789abcdef":
                        valid = False
                # Convert it
                if valid:
                    color_str = self.color.value.upper()
                    color = Colour.from_rgb(int(color_str[0:2], 16), int(color_str[2:4], 16), int(color_str[4:], 16))
            # Get color from RGB components
            elif len(self.r.value) > 0 and len(self.g.value) > 0 and len(self.b.value) > 0:
                r, g, b = int(self.r.value), int(self.g.value), int(self.b.value)

                if r >= 0 and g >= 0 and b >= 0 and r <= 255 and g <= 255 and b <= 255:
                    color = Colour.from_rgb(r, g, b)

        # Recreate embed
        embed: Embed = Embed(title=title, description=description, color=color)
        
        for field in original_embed.fields:
            embed.add_field(name=field.name, value=field.value)

        if len(original_embed.author.name) > 0:
            embed.set_author(name=original_embed.author.name)
        embed.set_footer(text=original_embed.footer.text)
        embed.set_image(url=original_embed.image.url)
        embed.set_thumbnail(url=original_embed.thumbnail.url)

        # Set image or thumbnail
        if self.target == "image":
            embed.set_image(self.url.value)
        if self.target == "thumbnail":
            embed.set_thumbnail(self.url.value)
        if self.target == "add field":
            embed.add_field(name=field_name, value=field_value, inline=self.inline.value.lower()[0] == "y")
        if self.target in ["edit field", "remove field"]:
            # Check if index is a number
            for char in self.index.value:
                if char not in "0123456789":
                    return

            # Check if index is lower than field count
            index = int(self.index.value) - 1
            if index >= len(embed.fields):
                return

            if self.target == "edit field":
                embed.set_field_at(index=index, name=field_name, value=field_value, inline=self.inline.value.lower()[0] == "y")
            else:
                embed.remove_field(index=index)
        if self.target == "footer":
            embed.set_footer(text=text)
        if self.target == "author":
            embed.set_author(name=text)

        await interaction.message.edit(embed=embed)


class Controls(View):
    def __init__(self):
        super().__init__()
        
        properties = ["Set Title", "Set Description", "Set Image", "Set Thumbnail", "Set Color", "Add Field", "Edit Field", "Remove Field", "Set Footer", "Set Author"]
        callbacks = [self.set_title, self.set_description, self.set_image, self.set_thumbnail, self.set_color, self.add_field, self.edit_field, self.remove_field, self.set_footer, self.set_author]

        for i in range(len(properties)):
            button: Button = Button(label=properties[i], style=ButtonStyle.gray, row=int(i-5 >= 0))
            button.callback = callbacks[i]
            self.add_item(button)

        button: Button = Button(label="Complete", style=ButtonStyle.green, row=2)
        button.callback = self.complete
        self.add_item(button)

        button: Button = Button(label="Discard", style=ButtonStyle.red, row=2)
        button.callback = self.discard
        self.add_item(button)
    

    async def set_title(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("title"))
    
    async def set_description(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("description"))

    async def set_image(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("image"))
    
    async def set_thumbnail(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("thumbnail"))
        
    async def set_color(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("color"))

    async def add_field(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("add field"))

    async def edit_field(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("edit field"))

    async def remove_field(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("remove field"))
    
    async def set_footer(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("footer"))
    
    async def set_author(self, interaction: Interaction):
        await interaction.response.send_modal(SetValueModal("author"))


    async def complete(self, interaction: Interaction):
        embed: Embed = interaction.message.embeds[0]
        await interaction.response.edit_message(embed=embed, view=None)
    

    async def discard(self, interaction: Interaction):
        await interaction.message.delete()


class EmbedCreator(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="Open embed designer.", force_global=PRODUCTION)
    async def create_embed(self, interaction: Interaction):
        self.logger.log_info(complete_name(interaction.user) + " has called command: create_embed.")

        embed: Embed = Embed(title="⠀")

        await interaction.response.send_message(embed=embed, view=Controls())


def load(client: commands.Bot):
    client.add_cog(EmbedCreator(client))