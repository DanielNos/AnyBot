import sys, nextcord, asyncio
from nextcord.ext import commands
from nextcord.ui import View, button, Button
from nextcord import Interaction, slash_command, VoiceClient, ButtonStyle

sys.path.append("../NosBot")
import logger as log
import dataManager

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()


class SoundBoardControls(View):
    def __init__(self):
        super().__init__()
    
    
    @button(label="Previous", style=ButtonStyle.gray)
    async def sound1(self, button: Button, interaction: Interaction):
        print(self.children)
        return


class SoundBoard(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
        self.playing = False
    

    @slash_command(guild_ids=TEST_GUILDS, description="Sound board.", force_global=PRODUCTION)
    async def sound_board(self, interaction: Interaction):

        await interaction.response.send_message("SOUND BOARD", view=SoundBoardControls(), ephemeral=True)


    @slash_command(guild_ids=TEST_GUILDS, description="Play the \"Hey, wake up!\" sound.", force_global=PRODUCTION)
    async def hey_wake_up(self, interaction: Interaction):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: hey_wake_up.")

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