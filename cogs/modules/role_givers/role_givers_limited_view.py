from logging import Logger, getLogger
from nextcord.ui import View, Button, button
from nextcord import ButtonStyle, Interaction


class LimitedBlueprintView(View):
    def __init__(self, editor_id: int):
        super().__init__(timeout=None)
        self.logger: Logger = getLogger("bot")
        self.editor_id = editor_id

    
    @button(label="Use /role_giver add_role [role] (text) (emoji)")
    async def add_role(self, button: Button, interaction: Interaction):
        await interaction.response.defer()

    
    @button(label="Remove Role", style=ButtonStyle.blurple, disabled=True)
    async def remove_role(self, button: Button, interaction: Interaction):

        await interaction.response.defer()

    
    @button(label="Complete", style=ButtonStyle.green, disabled=True)
    async def complete(self, button: Button, interaction: Interaction):

        await interaction.response.defer()
    

    @button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, button: Button, interaction: Interaction):

        # Allow only creator to edit
        if interaction.user.id != self.editor_id:
            await interaction.response.defer()
            return

        await interaction.message.delete()