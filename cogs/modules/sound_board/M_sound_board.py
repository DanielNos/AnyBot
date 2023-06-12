import os, sys
sys.path.append(os.path.dirname(__file__))

import logging
from logging import Logger
from discord.app_commands import command
from discord.ext.commands import Cog, Bot
from discord import Interaction, Embed
from discord.ui import View, Button
from sound_board_controls import SoundBoardControls
from sound_board_manager import SoundBoardManager


EMBED_COLOR: int = 0xBEF436
EMBED_THUMBNAIL_URL: str = "https://raw.githubusercontent.com/4lt3rnative/nosbot/main/sound_board.png"


class SoundBoard(Cog):
    def __init__(self, client):
        
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")

        self.sound_boards = {}
        self.sounds = []

        self.load_sounds()

    
    def load_sounds(self):
        if not os.path.exists("./modules_data/sound_board/"):
            os.mkdir("./modules_data/sound_board")

        for file in os.listdir("./modules_data/sound_board"):
            if not file.endswith(".mp3"):
                continue

            name = file.split("/")[-1][:-4]

            if name[0] == "0":
                button: Button = Button(label=name[1:])
            else:
                button: Button = Button(label=name[1:], emoji=name[0])

            self.sounds.append(button)

        self.logger.info(f"Loaded {len(self.sounds)} sounds to sound board.")
    

    def create_view(self, sound_board: SoundBoardManager) -> View:
        return SoundBoardControls(self.logger, sound_board, self.sounds)


    def create_embed(self, manager: SoundBoardManager) -> Embed:
        embed: Embed = Embed(title="Sound Board", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL_URL)

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