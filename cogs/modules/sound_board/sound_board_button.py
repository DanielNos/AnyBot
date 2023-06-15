import os, asyncio
from discord.ui import Button
from discord import ButtonStyle, Interaction, PCMVolumeTransformer, FFmpegPCMAudio, Embed, errors
from sound_board_manager import SoundBoardManager


QUEUE_SIZE: NotImplementedError = 3


class SoundBoardButton(Button):
    def __init__(self, manager: SoundBoardManager, label: str, emoji: str | None = None):
        super().__init__(label=label, emoji=emoji, style=ButtonStyle.gray)
        self.manager = manager

    
    async def callback(self, interaction: Interaction):

        # Check if bot is connected to voice
        await interaction.response.defer()
        if self.manager.voice_client == None:
            return

        # Construct path
        path = "./modules_data/sound_board/"
        if self.emoji != None:
            path += self.emoji.name
        else:
            path += "0"

        path += self.label + ".mp3"

        # Create sound name and path
        name = ""
        if self.emoji is not None:
            name += self.emoji.name

        name += self.label

        # Bot is playing
        if self.manager.voice_client.is_playing():
            # Add to queue
            if len(self.manager.queue) < QUEUE_SIZE:
                self.manager.queue.insert(0, (name, path))
            
            return

        # Play sound
        source = PCMVolumeTransformer(FFmpegPCMAudio(os.path.abspath(path)), self.manager.volume / 100)
        self.manager.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

<<<<<<< Updated upstream
        # Create sound name and path
        name = ""
        if self.emoji != None:
            path += self.emoji.name
        
        name += self.label
        
=======
        await self.update_indicator(name)

        # Play sounds from queue
        while len(self.manager.queue) > 0:
            name, path = self.manager.queue.pop()

            # Play sound
            source = PCMVolumeTransformer(FFmpegPCMAudio(os.path.abspath(path)), self.manager.volume / 100)
            
            # Wait for end
            while self.manager.voice_client.is_playing():
                await asyncio.sleep(0.1)
            
            self.manager.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

            await self.update_indicator(name)
        
    
    async def update_indicator(self, name: str):
>>>>>>> Stashed changes
        # Change currently playing indicator in all messages
        embed: Embed = self.manager.messages[0].embeds[0]
        embed.set_field_at(index=2, name="Playing:", value=name, inline=False)
        embed.set_field_at(index=3, name="Queue:", value=self.manager.queue_str(), inline=False)

        for i in range(len(self.manager.messages)-1, -1, -1):            
            try:
                await self.manager.messages[i].edit(embed=embed)
            except errors.NotFound:
                del self.manager.messages[i]

        # Wait for end
        while self.manager.voice_client.is_playing():
            await asyncio.sleep(0.1)

        # Change currently playing indicator to "nothing" in all messages
        embed.set_field_at(index=2, name="Playing:", value="nothing", inline=False)
        for i in range(len(self.manager.messages)-1, -1, -1):            
            try:
                await self.manager.messages[i].edit(embed=embed)
            except errors.NotFound:
                del self.manager.messages[i]