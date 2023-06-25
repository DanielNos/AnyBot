from logging import Logger
from nextcord.ui import View, Button, button
from nextcord import ButtonStyle, Interaction
from role_givers_modals import AddRoleModal
from emoji import is_emoji


NUMBERS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]


class RoleGiverDelete(View):
    def __init__(self):
        super().__init__(timeout=None)

    
    @button(label="Yes, delete it", style=ButtonStyle.red)
    async def delete(self, button: Button, interaction: Interaction):
        pass


    @button(label="No, keep it", style=ButtonStyle.green)
    async def keep(self, button: Button, interaction: Interaction):
        pass


class RoleGiverView(View):
    def __init__(self, logger: Logger, cog):
        super().__init__(timeout=None)
        self.logger = logger

        self.button_add_role: Button = self.children[0]
        self.button_remove_role: Button = self.children[1]
        self.button_complete: Button = self.children[2]

        self.roles = []

    
    @button(label="Use /role_giver add_role")
    async def add_role(self, button: Button, interaction: Interaction):

        modal = AddRoleModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        text = modal.input.value

        # Collect emoji
        emoji = NUMBERS[len(self.roles)]
        if is_emoji(text[0]):
            emoji = text[0]
            text = text[1:]

        # Check for duplicate emoji
        for role in self.roles:
            if role[1] == emoji:
                return
        
        text = text.strip()
        
        # Save role
        self.roles.append((text, emoji))

        # Update GUI
        if len(self.roles) == 9:
            self.button_add_role.disabled = True
        
        self.button_complete.disabled = False

        await interaction.edit_original_message(content=f"{interaction.message.content}\n{emoji} {text}", view=self)

    
    @button(label="Remove Role", style=ButtonStyle.blurple)
    async def remove_role(self, button: Button, interaction: Interaction):

        await interaction.response.send_modal()

    
    @button(label="Complete", style=ButtonStyle.green, disabled=True)
    async def complete(self, button: Button, interaction: Interaction):

        await interaction.response.send_modal()
    

    @button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, button: Button, interaction: Interaction):

        await interaction.message.delete()