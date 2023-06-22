from typing import List
from nextcord.ui import Modal, TextInput
from nextcord import Interaction


class InputsModal(Modal):
    def __init__(self, inputs: List[TextInput]) -> None:
        super().__init__(title="Embed Editor")

        self.inputs = inputs

        for input in inputs:
            self.add_item(input)
    

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        self.stop()