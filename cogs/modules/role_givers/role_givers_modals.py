from nextcord import Interaction
from nextcord.ui import Modal, TextInput
from nextcord import TextInputStyle


class AddRoleModal(Modal):
    def __init__(self):
        super().__init__(title="Add Role")
        
        self.input = TextInput(label="Role Text", style=TextInputStyle.paragraph, required=True, min_length=5, max_length=100, placeholder="Start with a emoji if you want to vote using it (instead of number).")
        self.add_item(self.input)

    
    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        self.stop()