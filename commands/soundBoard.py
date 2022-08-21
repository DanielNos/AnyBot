import sys, nextcord, asyncio
from nextcord.ext import commands
from nextcord.ui import View, Button
from nextcord import Interaction, slash_command, VoiceClient, ButtonStyle

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import complete_name

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()
SOUNDS = dataManager.load_sounds()
ACTIVE_USERS = []


class SoundBoardControls(View):
    def __init__(self, client: commands.Bot, logger: log.Logger):
        super().__init__()
        self.client = client
        self.page = 0
        self.logger = logger
        self.player = None

        # Create sounds grid
        callbacks = [self.play_0, self.play_1, self.play_2, self.play_3, self.play_4, self.play_5, self.play_6, self.play_7, self.play_8, self.play_9, self.play_10, self.play_11, self.play_12, self.play_13, self.play_14]

        index = 0
        for y in range(3):
            for x in range(5):
                label = " "
                if index < len(SOUNDS[0].keys()):
                    label = list(SOUNDS[0].keys())[index]

                button: Button = Button(style=ButtonStyle.gray, row=y, label=label, disabled=(label == " "))
                button.callback = callbacks[index]
                self.add_item(button)
                index += 1
        
        # Add page controls
        button: Button = Button(style=ButtonStyle.blurple, row=4, label="Previous", disabled=True)
        button.callback = self.previous
        self.add_item(button)

        button = Button(style=ButtonStyle.gray, row=4, label="1/" + str(len(SOUNDS)))
        button.callback = self.next
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.blurple, row=4, label="Next", disabled=(len(SOUNDS) == 1))
        button.callback = self.next
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.green, row=4, label="Connect")
        button.callback = self.connect
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.red, row=4, label="Disconnect")
        button.callback = self.disconnect
        self.add_item(button)
    

    async def connect(self, interaction: Interaction):
        if self.player:
            await self.player.connect()
            self.player = None
        await interaction.response.defer()


    async def disconnect(self, interaction: Interaction):
        if self.player:
            await self.player.disconnect()
            self.player = None
        await interaction.response.defer()
    

    # Callbacks
    async def play_0(self, interaction: Interaction):
        await self.play_sound(interaction, 0)
    
    async def play_1(self, interaction: Interaction):
        await self.play_sound(interaction, 1)

    async def play_2(self, interaction: Interaction):
        await self.play_sound(interaction, 2)

    async def play_3(self, interaction: Interaction):
        await self.play_sound(interaction, 3)

    async def play_4(self, interaction: Interaction):
        await self.play_sound(interaction, 4)

    async def play_5(self, interaction: Interaction):
        await self.play_sound(interaction, 5)

    async def play_6(self, interaction: Interaction):
        await self.play_sound(interaction, 6)

    async def play_7(self, interaction: Interaction):
        await self.play_sound(interaction, 7)

    async def play_8(self, interaction: Interaction):
        await self.play_sound(interaction, 8)

    async def play_9(self, interaction: Interaction):
        await self.play_sound(interaction, 9)

    async def play_10(self, interaction: Interaction):
        await self.play_sound(interaction, 10)

    async def play_11(self, interaction: Interaction):
        await self.play_sound(interaction, 11)

    async def play_12(self, interaction: Interaction):
        await self.play_sound(interaction, 12)

    async def play_13(self, interaction: Interaction):
        await self.play_sound(interaction, 13)

    async def play_14(self, interaction: Interaction):
        await self.play_sound(interaction, 14)
    
    async def previous(self, interaction: Interaction):
        await self.change_page(interaction, -1)

    async def next(self, interaction: Interaction):
        await self.change_page(interaction, 1)


    async def play_sound(self, interaction: Interaction, index: int):
        global ACTIVE_USERS

        # Log
        sound_name = list(SOUNDS[self.page].keys())[index]
        self.logger.log_info(complete_name(interaction.user) + " has triggered sound board: " + sound_name + ".")
        
        voice = interaction.user.voice

        # Return if user isn't in a voice channel
        if voice == None:
            await interaction.response.edit_message(content="```You have to be connected to a voice channel to use the sound board.```", view=self)
            return
        
        if interaction.user.id in ACTIVE_USERS:
            await interaction.response.defer()
            return

        # Add experience
        dataManager.add_experience(interaction.user.id, "sound board")

        ACTIVE_USERS.append(interaction.user.id)

        # Connect to voice channel
        if not self.player:
            self.player = await voice.channel.connect()
        await interaction.response.edit_message(content="PLAYED: ``" + sound_name + "``", view=self)

        # Load sound
        file_name = list(SOUNDS[self.page].values())[index]
        exe = "./command_data/sound_board/ffmpeg/bin/ffmpeg.exe" * (not PRODUCTION) or "ffmpeg" * PRODUCTION
        
        # Play sound
        source = nextcord.FFmpegPCMAudio(source=file_name, executable=exe)
        self.player.play(source)

        # Wait until sound finishes
        while self.player.is_playing():
            await asyncio.sleep(0.1)
        
        # Remove from active
        ACTIVE_USERS.remove(interaction.user.id)


    async def change_page(self, interaction: Interaction, move: int):
        next_page = self.page + move

        # Change page
        if next_page >= 0 and next_page <= len(SOUNDS)-1:
            self.page += move
        else:
            await interaction.response.defer()
            return
        
        # Enable/Disable buttons
        self.children[15].disabled = (self.page == 0)
        self.children[17].disabled = (self.page == len(SOUNDS)-1)

        # Update buttons
        keys = list(SOUNDS[self.page].keys())

        for i in range(15):
            label = "-"
            if i < len(SOUNDS[self.page].keys()):
                label = keys[i]
            
            self.children[i].label = label
            self.children[i].disabled = (label == " ")
        
        self.children[16].label = str(self.page+1) + "/" + str(len(SOUNDS)+1)

        await interaction.response.edit_message(view=self)


class SoundBoard(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
        self.playing = False
    

    @slash_command(guild_ids=TEST_GUILDS, description="Sound board.", force_global=PRODUCTION)
    async def sound_board(self, interaction: Interaction):
        self.logger.log_info(complete_name(interaction.user) + " has called command: sound_board.")

        await interaction.response.send_message(view=SoundBoardControls(self.client, self.logger), ephemeral=True)


    @slash_command(guild_ids=TEST_GUILDS, description="Play the \"Hey, wake up!\" sound.", force_global=PRODUCTION)
    async def hey_wake_up(self, interaction: Interaction):
        self.logger.log_info(complete_name(interaction.user) + " has called command: hey_wake_up.")

        # Try to find users voice channel
        voice = interaction.user.voice

        # Return if bot is already playing
        if self.playing:
            await interaction.response.send_message("🚫 FAILED. NosBot is currently playing in a channel. Try again once it finishes.", ephemeral=True)

        # Play if user is in a voice channel
        if voice != None:
            await interaction.response.send_message("✅ Your message is being played.", ephemeral=True)
            self.playing = True

            # Connect to voice channel
            player: VoiceClient = await voice.channel.connect()

            # Play
            exe = "./command_data/sound_board/ffmpeg/bin/ffmpeg.exe" * (not PRODUCTION) or "ffmpeg" * PRODUCTION
            source = nextcord.FFmpegPCMAudio(source="./command_data/sound_board/hey_wake_up.mp3", executable=exe)
            player.play(source)

            # Disconnect
            await asyncio.sleep(2)
            await player.disconnect()

            self.playing = False
        else:
            await interaction.response.send_message("🚫 FAILED. You are not in a voice channel.", ephemeral=True)


def load(client: commands.Bot):
    client.add_cog(SoundBoard(client))