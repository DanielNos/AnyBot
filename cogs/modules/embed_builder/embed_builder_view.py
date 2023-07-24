from logging import Logger
from typing import List
from formatting import get_place
from nextcord import Embed, ButtonStyle, Interaction, TextInputStyle
from nextcord.ui import View, Button, TextInput, button
from embed_builder_modals import InputsModal


async def CreateModal(interaction: Interaction, inputs: List[TextInput]) -> List[str]:
    
    # Create modal and wait until it's submitted
    modal = InputsModal(inputs)
    await interaction.response.send_modal(modal)
    await modal.wait()
        
    return [input.value for input in modal.inputs]


class EmbedBuilderEditor(View):
    def __init__(self, logger: Logger, embed: Embed, creator_id: int):
        super().__init__(timeout=None)
        self.logger = logger
        self.embed: Embed = embed
        self.creator_id = creator_id
        self.allow_only_creator = True

        self.button_add_field: Button = self.children[6]
        self.button_remove_field: Button = self.children[7]


    @button(label="Set title")
    async def set_title(self, button: Button, interaction: Interaction):

        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        values = await CreateModal(interaction, [
            TextInput(label="Title", max_length=256, style=TextInputStyle.paragraph)
        ])
        self.embed.title = values[0]
        
        await interaction.edit(embed=self.embed)


    @button(label="Set description")
    async def set_description(self, button: Button, interaction: Interaction):
        
        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        values = await CreateModal(interaction, [
            TextInput(label="Description", max_length=2048, style=TextInputStyle.paragraph, required=True)
        ])
        self.embed.description = values[0]
        
        await interaction.edit(embed=self.embed)


    @button(label="Set footer")
    async def set_footer(self, button: Button, interaction: Interaction):
        
        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        # Collect values
        values = await CreateModal(interaction, [
            TextInput(label="Footer Text", max_length=2048, style=TextInputStyle.paragraph),
            TextInput(label="Footer Icon URL", max_length=1024, style=TextInputStyle.paragraph, required=False)
        ])

        # Set footer
        if len(values[1]) == 0:
            values[1] = None

        self.embed.set_footer(text=values[0], icon_url=values[1])
        
        await interaction.edit(embed=self.embed)


    @button(label="Set thumbnail")
    async def set_thumbnail(self, button: Button, interaction: Interaction):
        
        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        values = await CreateModal(interaction, [
            TextInput(label="Thumbnail Image URL", max_length=1024, style=TextInputStyle.paragraph, required=True)
        ])
        self.embed.set_thumbnail(values[0])
        
        await interaction.edit(embed=self.embed)

    
    @button(label="Set image")
    async def set_image(self, button: Button, interaction: Interaction):

        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        # Collect value
        values = await CreateModal(interaction, [
            TextInput(label="Image URL", max_length=1024, style=TextInputStyle.paragraph, required=True)
        ])
        self.embed.set_image(values[0])
        
        await interaction.edit(embed=self.embed)

    
    @button(label="Set color")
    async def set_color(self, button: Button, interaction: Interaction):

        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        # Collect value
        values = await CreateModal(interaction, [
            TextInput(label="Color Hex Code", min_length=7, max_length=7, required=True, placeholder="#00AABB")
        ])

        color = values[0].lower()

        # Check if color code is valid
        if len(color) != 7:
            return
        
        if color[0] != "#":
            return

        color = color[1:]
        
        for char in color:
            if char not in "0123456789abcdef":
                return
        
        # Change color
        self.embed.color = int(color, 16)
        await interaction.edit(embed=self.embed)


    @button(label="Add field")
    async def add_field(self, button: Button, interaction: Interaction):
        
        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        # Collect values
        values = await CreateModal(interaction, [
            TextInput(label="Name", max_length=256, required=True),
            TextInput(label="Value", max_length=1024, required=True, style=TextInputStyle.paragraph),
            TextInput(label="Inline", max_length=3, required=True, default_value="yes", placeholder="yes/no")
        ])

        # Add field
        inline = True if values[2].lower()[0] == "y" else False
        self.embed.add_field(name=values[0], value=values[1], inline=inline)

        # Change button states
        self.button_remove_field.disabled = False

        if len(self.embed.fields) >= 25:
            button.disabled = True

        # Edit message
        await interaction.edit(embed=self.embed, view=self)
    

    @button(label="Remove field", disabled=True)
    async def remove_field(self, button: Button, interaction: Interaction):
        
        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.defer()
            return

        # Remove field if it's the only one
        if len(self.embed.fields) == 1:
            self.embed.remove_field(0)
            button.disabled = True

            await interaction.edit(embed=self.embed, view=self)
            return
        
        # Collect values
        values = await CreateModal(interaction, [
            TextInput(label=f"Field Number (1 - {len(self.embed.fields)})", max_length=2, required=True)
        ])

        # Check if index is correct
        indexes = [str(i) for i in range(1, len(self.embed.fields) + 1)]

        if values[0] not in indexes:
            return
        
        # Remove field
        self.button_add_field.disabled = False
        self.embed.remove_field(int(values[0]) - 1)
        await interaction.edit(embed=self.embed, view=self)


    @button(label="Can edit: Creator", style=ButtonStyle.blurple)
    async def editor(self, button: Button, interaction: Interaction):
        
        # Allow only creator to change this
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return
        
        # Change who can edit embed
        self.allow_only_creator = not self.allow_only_creator
        
        # Edit button
        if self.allow_only_creator:
            button.label = "Can edit: Creator"
        else:
            button.label = "Can edit: Everyone"
        
        await interaction.response.edit_message(view=self)


    @button(label="Delete", style=ButtonStyle.red)
    async def delete(self, button: Button, interaction: Interaction):
        
        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        await interaction.message.delete()
    

    @button(label="Finish", style=ButtonStyle.green)
    async def finish(self, button: Button, interaction: Interaction):

        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        await interaction.edit(view=None)
        self.logger.info(f"{interaction.user.name} has completed a embed in {get_place(interaction)}.")
    

    @button(label="Finish (post as new)", style=ButtonStyle.green)
    async def finish_as_new(self, button: Button, interaction: Interaction):

        # Allow only permitted users
        if self.allow_only_creator and interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return

        await interaction.channel.send(embed=self.embed)
        await interaction.message.delete()