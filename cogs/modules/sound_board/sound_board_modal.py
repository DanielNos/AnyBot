from nextcord.ui import Modal, TextInput
from nextcord import Interaction


class VolumeModal(Modal):
    def __init__(self, view):
        super().__init__(title="Change Volume")
        self.view = view

        self.volume: TextInput = TextInput(label="Volume", placeholder=100, default_value=100, min_length=1, max_length=3)
        self.add_item(self.volume)
    

    async def callback(self, interaction: Interaction):
        # Invalid number
        for char in self.volume.value:
            if not char in "0123456789":
                await interaction.response.defer()
                return

        # Clamp value
        volume: int = int(self.volume.value)
        
        if volume > 150:
            volume = 150
        
        # Update value
        await self.view.set_volume(volume)
        await interaction.response.defer()