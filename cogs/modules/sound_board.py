import logging
from logging import Logger
from discord.app_commands import command
from discord.ext.commands import Cog, Bot
from discord import Interaction, Embed, ButtonStyle, VoiceClient, errors
from discord.ui import View, Button, Modal, TextInput, button


class SoundBoardManager:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.voice_client: VoiceClient | None = None
        self.playing: str | None = None
        self.volume: int = 100
        self.messages = []
        

class SoundBoardControls(View):
    def __init__(self, logger: Logger, manager: SoundBoardManager):
        super().__init__(timeout=None)
        self.logger = logger

        self.manager: SoundBoardManager = manager

        # Assign buttons
        self.button_connect: Button = self.children[0]
        self.button_disconnect: Button = self.children[1]
        self.button_volume_down: Button = self.children[2]
        self.button_custom_volume: Button = self.children[3]
        self.button_volume_up: Button = self.children[4]

        if manager.voice_client != None:
            self.button_disconnect.disabled = False

    
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


    async def update_volume_buttons(self):
        # Disable/Enable volume buttons
        if self.manager.volume >= 150:
            self.button_volume_up.disabled = True
            await self.update_view()
        elif self.button_volume_up.disabled:
            self.button_volume_up.disabled = False
            await self.update_view()

        if self.manager.volume <= 0:
            self.button_volume_down.disabled = True
            await self.update_view()
        elif self.button_volume_down.disabled:
            self.button_volume_down.disabled = False
            await self.update_view()


    async def set_channel(self, channel: str = None):
        # Edit embed
        embed: Embed = self.manager.messages[0].embeds[0]

        if channel != None:
            embed.set_field_at(index=0, name="Connected to:", value=channel)
        else:
            embed.set_field_at(index=0, name="Not connected", value="")
        
        await self.update_embed(embed)


    async def change_volume(self, change: int):
        await self.set_volume(self.manager.volume + change)

    
    async def set_volume(self, volume: int):
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

        await self.update_volume_buttons()


    @button(label="Connect", style=ButtonStyle.green)
    async def connect(self, interaction: Interaction, button: Button):
        
        # User is not connected to a voice channel
        if interaction.user.voice == None:
            await interaction.response.send_message("You have to be connected to a voice channel.", ephemeral=True)
            return
    
        # Connect to channel
        if self.manager.voice_client == None:
            self.logger.info(f"Connecting to \"{interaction.user.voice.channel.name}\" voice channel at {interaction.user.guild.name}.")
            self.manager.voice_client = await interaction.user.voice.channel.connect(self_deaf=True)
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
    

    @button(label="Disconnect", style=ButtonStyle.red, disabled=True)
    async def disconnect(self, interaction: Interaction, button: Button):
        
        # Disconnect
        if self.manager.voice_client != None:
            await self.manager.voice_client.disconnect()
            self.manager.voice_client = None

        # Update button
        button.disabled = True
        await self.update_view()

        # Update text
        await self.set_channel()

        await interaction.response.defer()

    
    @button(label="", emoji="🔉", style=ButtonStyle.gray)
    async def volume_down(self, interaction: Interaction, button: Button):
        
        if self.manager.volume > 0:
            await self.change_volume(-10)

        await interaction.response.defer()

    
    @button(label="", emoji="⚙️", style=ButtonStyle.gray)
    async def custom_volume(self, interaction: Interaction, button: Button):
        
        await interaction.response.send_modal(CustomVolume(self))
    

    @button(label="", emoji="🔊", style=ButtonStyle.gray)
    async def volume_up(self, interaction: Interaction, button: Button):

        if self.manager.volume < 150:
            await self.change_volume(10)
        
        await interaction.response.defer()


class CustomVolume(Modal):
    def __init__(self, view: SoundBoardControls):
        super().__init__(title="Custom Volume")
        self.view: SoundBoardControls = view

        self.volume: TextInput = TextInput(label="Volume", placeholder=100, default=100, min_length=1, max_length=3)
        self.add_item(self.volume)
    

    async def on_submit(self, interaction: Interaction):
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


class SoundBoard(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")

        self.sound_boards = {}
    

    def create_view(self, sound_board: SoundBoardManager) -> View:
        return SoundBoardControls(self.logger, sound_board)


    def create_embed(self, manager: SoundBoardManager) -> Embed:
        embed: Embed = Embed(title="Sound Board", color=0xBEF436)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/4lt3rnative/nosbot/main/sound_board.png")

        if manager.voice_client == None:
            embed.add_field(name="Not connected", value="", inline=False)
        else:
            embed.add_field(name="Connected to", value=manager.voice_client.channel.name, inline=False)

        embed.add_field(name="Volume:", value=str(manager.volume) + "%")

        if manager.playing == None:
            embed.add_field(name="Playing:", value="nothing", inline=False)
        else:
            embed.add_field(name="Playing:", value=manager.playing, inline=False)

        return embed


    @command(name="sound_board", description="Opens sound board.")
    async def sound_board(self, interaction: Interaction):
        
        # Called outside of guild
        if interaction.guild_id == None:
            return

        # Get sound board
        if interaction.guild_id in self.sound_boards:
            sound_board = self.sound_boards[interaction.guild_id]
        # Create a new one if it doesn't exist
        else:
            sound_board = SoundBoardManager(interaction.guild_id)
            self.sound_boards[interaction.guild_id] = sound_board

        await interaction.response.send_message(embed=self.create_embed(sound_board), view=self.create_view(sound_board))
        sound_board.messages.append(await interaction.original_response())


async def setup(client):
    await client.add_cog(SoundBoard(client))