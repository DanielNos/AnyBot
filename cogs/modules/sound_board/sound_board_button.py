import os, asyncio
from discord.ui import Button
from discord import ButtonStyle, Interaction, PCMVolumeTransformer, FFmpegPCMAudio, Embed, errors
from discord.ext.commands import Bot
from sound_board_manager import SoundBoardManager


class SoundBoardButton(Button):
    def __init__(self, manager: SoundBoardManager, label: str, emoji: str | None = None):
        super().__init__(label=label, emoji=emoji, style=ButtonStyle.gray)
        self.manager = manager

    
    async def callback(self, interaction: Interaction):

        # Check if bot is connected to voice and isn't playing
        await interaction.response.defer()
        if self.manager.voice_client == None or self.manager.voice_client.is_playing():
            return

        # Construct path
        path = "./modules_data/sound_board/"
        if self.emoji != None:
            path += self.emoji.name
        else:
            path += "0"

        path += self.label + ".mp3"

        # Play sound
        source = PCMVolumeTransformer(FFmpegPCMAudio(os.path.abspath(path)), self.manager.volume / 100)
        self.manager.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        # Update playing indicator
        name = ""
        if self.emoji != None:
            path += self.emoji.name
        
        name += self.label

        embed: Embed = self.manager.messages[0].embeds[0]
        embed.set_field_at(index=2, name="Playing:", value=name, inline=False)

        for i in range(len(self.manager.messages)-1, -1, -1):            
            try:
                await self.manager.messages[i].edit(embed=embed)
            except errors.NotFound:
                del self.manager.messages[i]

        # Wait for end
        while self.manager.voice_client.is_playing():
            await asyncio.sleep(0.1)

        # Change indicator
        embed.set_field_at(index=2, name="Playing:", value="nothing", inline=False)
        for i in range(len(self.manager.messages)-1, -1, -1):            
            try:
                await self.manager.messages[i].edit(embed=embed)
            except errors.NotFound:
                del self.manager.messages[i]