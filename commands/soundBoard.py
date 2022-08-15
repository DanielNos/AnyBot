import sys, nextcord, asyncio
from nextcord.ext import commands
from nextcord import Interaction, slash_command, VoiceClient

sys.path.append("../NosBot")
import logger as log
import dataManager

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

class SoundBoard(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
        self.playing = False
    

    @slash_command(guild_ids=TEST_GUILDS, description="Play a \"Hey, wake up!\" sound.", force_global=PRODUCTION)
    async def hey_wake_up(self, interaction: Interaction):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: hey_wake_up.")

        # Try to find users voice channel
        voice_channel = interaction.user.voice.channel

        # Return if bot is already playing
        if self.playing:
            await interaction.response.send_message("🚫 FAILED. NosBot is currently playing in a channel. Try again once it finishes.", ephemeral=True)

        # Play if user is in a voice channel
        if voice_channel != None:
            await interaction.response.send_message("✅ Your message is being played.", ephemeral=True)
            self.playing = True

            # Connect to voice channel
            player: VoiceClient = await voice_channel.connect()

            # Play
            exe = "./command_data/sound_board/ffmpeg/bin/ffmpeg.exe"
            if PRODUCTION:
                exe = "ffmpeg"
                
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