from logging import Logger
from nextcord import Embed, ButtonStyle, Interaction, errors
from nextcord.ui import View, Button, button
from math import ceil
from sound_board_manager import SoundBoardManager
from cogs.modules.sound_board.sound_board_modal import VolumeModal
from sound_board_button import SoundBoardButton


PAGE_SIZE: int = 19 # The amount of buttons on one page. (1 - 19)


class SoundBoardControls(View):
    def __init__(self, logger: Logger, manager: SoundBoardManager, sounds):
        super().__init__(timeout=None)
        self.logger = logger

        self.manager: SoundBoardManager = manager
        self.sounds = sounds
        self.page = 0
        self.page_count = ceil(len(sounds) / PAGE_SIZE)
        self.current_buttons = []

        # Assign buttons
        self.button_connect: Button = self.children[0]
        self.button_disconnect: Button = self.children[1]
        self.button_prev_page: Button = self.children[2]
        self.button_page_counter: Button = self.children[3]
        self.button_next_page: Button = self.children[4]
        
        # Set button states
        if manager.voice_client != None:
            self.button_disconnect.disabled = False

        self.update_page_buttons()
        self.create_page()


    def create_page(self):
        if self.page > self.page_count:
            return
        
        # Create range for page
        start: int = self.page * PAGE_SIZE
        end: int = start + PAGE_SIZE

        if len(self.sounds) < end:
            end = len(self.sounds)

        # Remove all buttons
        for button in self.current_buttons:
            self.remove_item(button)
        self.current_buttons.clear()

        # Load new buttons
        for i in range(start, end):
            button: SoundBoardButton = SoundBoardButton(self.manager, self.sounds[i][1], self.sounds[i][0])
            self.add_item(button)
            self.current_buttons.append(button)


    def update_page_buttons(self):
        self.button_page_counter.label = str(self.page + 1) + "/" + str(self.page_count)
        self.button_next_page.disabled = self.page == self.page_count - 1
        self.button_prev_page.disabled = self.page == 0

    
    async def update_view(self):
        # Update messages
        for i in range(len(self.manager.messages)-1, -1, -1):
            try:
                await self.manager.messages[i].edit(view=self)
            except errors.NotFound:
                del self.manager.messages[i]

    
    async def update_embed(self, embed: Embed):
        # Update messages
        for i in range(len(self.manager.messages)-1, -1, -1):         
            try:
                await self.manager.messages[i].edit(embed=embed)
            except errors.NotFound:
                del self.manager.messages[i]


    async def set_channel(self, channel: str = None):
        # Edit embed
        embed: Embed = self.manager.messages[0].embeds[0]

        if channel != None:
            embed.set_field_at(index=0, name="Connected to:", value=channel)
        else:
            embed.set_field_at(index=0, name="Not connected", value="")
        
        await self.update_embed(embed)

    
    async def set_volume(self, volume: int, member_name: str):
        # Clamp value
        if volume > 150:
            volume = 150
        elif volume < 0:
            volume = 0

        self.manager.volume = volume

        # Edit embed
        embed: Embed = self.manager.messages[0].embeds[0]
        embed.set_field_at(index=1, name="Volume:", value=str(self.manager.volume) + "%")

        await self.update_embed(embed)
        self.logger.info(f"Sound board volume was set to {volume} by {member_name}.")


    @button(label="Connect", style=ButtonStyle.green)
    async def connect(self, button: Button, interaction: Interaction):

        # User is not connected to a voice channel
        if interaction.user.voice is None:
            await interaction.response.send_message("You have to be connected to a voice channel.", ephemeral=True)
            return
    
        # Connect to channel
        if self.manager.voice_client is None:
            self.logger.info(f"Connecting to \"{interaction.user.voice.channel.name}\" voice channel at {interaction.user.guild.name}.")
            self.manager.voice_client = await interaction.user.voice.channel.connect()
            print(self.manager.voice_client.channel)
        # Change channel
        elif self.manager.voice_client.channel != interaction.user.voice.channel:
            self.logger.info(f"Moving from \"{self.manager.voice_client.channel.name}\" to \"{interaction.user.voice.channel.name}\" voice channel at {interaction.user.guild.name}.")
            await self.manager.voice_client.move_to(interaction.user.voice.channel)

        # Enable disconnect
        self.button_disconnect.disabled = False
        await self.update_view()

        # Update text
        await self.set_channel(self.manager.voice_client.channel.name)

        await interaction.response.defer()

        self.logger.info(f"Bot was connected to voice channel {interaction.user.voice.channel.guild.name}/{interaction.user.voice.channel.name} by {interaction.user.name}.")
    

    @button(label="Disconnect", style=ButtonStyle.red, disabled=True)
    async def disconnect(self, button: Button, interaction: Interaction):
        
        # Disconnect
        if self.manager.voice_client is not None:
            await self.manager.voice_client.disconnect()
            self.manager.voice_client = None
            self.manager.queue.clear()

        # Update button
        button.disabled = True
        await self.update_view()

        # Update text
        await self.set_channel()

        await interaction.response.defer()

        self.logger.info(f"Bot was disconnected from voice channel by {interaction.user.name}.")

    
    @button(label="", emoji="⬅️", style=ButtonStyle.gray, disabled=True)
    async def prev_page(self, button: Button, interaction: Interaction):

        # Move to previous page and render it
        if self.page > 0:
            self.page -= 1
            self.create_page()

        # Update buttons and page
        self.update_page_buttons()
        await self.update_view()

        await interaction.response.defer()
        
        await interaction.response.defer()

    
    @button(label="1/1", style=ButtonStyle.gray)
    async def current_page(self, button: Button, interaction: Interaction):
        
        await interaction.response.defer()


    @button(label="", emoji="➡️", style=ButtonStyle.gray)
    async def next_page(self, interaction: Interaction, button: Button):
        
        # Move to next page and render it
        if self.page < self.page_count - 1:
            self.page += 1
            self.create_page()

        # Update buttons and page
        self.update_page_buttons()
        await self.update_view()

        await interaction.response.defer()


    @button(label="", emoji="🔊", style=ButtonStyle.blurple)
    async def custom_volume(self, button: Button, interaction: Interaction):
        
        await interaction.response.send_modal(VolumeModal(self))