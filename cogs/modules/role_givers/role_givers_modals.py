from logging import Logger, getLogger
from nextcord import Interaction
from nextcord.ui import Modal, TextInput
from role_giver import RoleGiverBlueprint
from role_givers_limited_view import LimitedBlueprintView


class RemoveRoleModal(Modal):
    def __init__(self, blueprint: RoleGiverBlueprint):
        super().__init__(title="Add Role")
        self.logger: Logger = getLogger("bot")
        self.blueprint: RoleGiverBlueprint = blueprint
        
        self.input = TextInput(label=f"Role Number (1 - {len(blueprint.roles)})", required=True, min_length=1, max_length=2)
        self.add_item(self.input)

    
    async def callback(self, interaction: Interaction):
        # Check if value is number
        for char in self.input.value:
            if char not in "0123456789":
                await interaction.response.defer()
                return

        # Check if value is in correct range
        index = int(self.input.value)
        if index < 1 or index > len(self.blueprint.roles):
            await interaction.response.defer()
            return

        # Remove role
        lines = interaction.message.content.split("\n")

        del lines[index]
        del self.blueprint.roles[index - 1]

        # Disable buttons when no roles
        if len(self.blueprint.roles) == 0:
            await interaction.response.edit_message(content="".join(lines), view=LimitedBlueprintView())
        else:
            await interaction.response.edit_message(content="".join(lines))