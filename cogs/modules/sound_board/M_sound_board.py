import os, sys
sys.path.append(os.path.dirname(__file__))

import logging
from logging import Logger
from nextcord.ext.commands import Cog, Bot
from nextcord import Interaction, Embed, Attachment, slash_command
from nextcord.ui import View
from cogs.modules.sound_board.sound_board_view import SoundBoardControls
from sound_board_manager import SoundBoardManager
from emoji import is_emoji
import config


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
        # Create folder
        if not os.path.exists("./modules_data/sound_board/"):
            os.mkdir("./modules_data/sound_board")

        # Load sound names
        for file in os.listdir("./modules_data/sound_board"):
            if not file.endswith(".mp3"):
                continue

            name = file.split("/")[-1][:-4]

            if name[0] == "0":
                self.sounds.append((None, name[1:]))
            else:
                self.sounds.append((name[0], name[1:]))

        self.logger.info(f"Loaded {len(self.sounds)} sounds to sound board.")
    

    def create_view(self, sound_board: SoundBoardManager) -> View:
        return SoundBoardControls(self.logger, sound_board, self.sounds)


    def create_embed(self, manager: SoundBoardManager) -> Embed:
        # Create embed
        embed: Embed = Embed(title="Sound Board", color=EMBED_COLOR)
        embed.set_thumbnail(url=EMBED_THUMBNAIL_URL)

        # Current connection field
        if manager.voice_client == None:
            embed.add_field(name="Not connected", value="", inline=False)
        else:
            embed.add_field(name="Connected to", value=manager.voice_client.channel.name, inline=False)

        # Volume field
        embed.add_field(name="Volume:", value=str(manager.volume) + "%")

        # Currently playing field
        if manager.playing == None:
            embed.add_field(name="Playing:", value="nothing", inline=False)
        else:
            embed.add_field(name="Playing:", value=manager.playing, inline=False)

        # Queue field
        embed.add_field(name="Queue:", value=manager.queue_str())

        return embed


    @slash_command(name="sound_board", description="Opens sound board.", guild_ids=config.DEBUG["test_guilds"])
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
        sound_board.messages.append(await interaction.original_message())

        self.logger.info(f"{interaction.user.name} has opened a sound board in {interaction.guild.name}/{interaction.channel.name}.")

    
    @slash_command(name="upload_sound", description="Uploads a sound to sound board.", guild_ids=config.DEBUG["test_guilds"])
    async def upload_sound(self, interaction:Interaction, sound: Attachment, emoji: str = ""):
        
        # Check if user is allowed to upload
        if interaction.user.id not in [277796227397976064, 533327218403835905]:
            await interaction.response.send_message("❌ You don't have rights! 😅")
            return
        
        # No mp3 extension
        if not sound.filename.endswith(".mp3"):
            await interaction.response.send_message("❌ Invalid file format. Only .mp3 files are allowed.")
            return
        
        # Invalid emoji
        if emoji != "" and not is_emoji(emoji):
            await interaction.response.send_message("❌ Invalid emoji.")
            return
        
        # Construct file name and button label
        if emoji != "":
            name = emoji[0] + sound.filename
            entry_name = emoji[0] + " " + sound.filename[:-4]
        else:
            name = "0" + sound.filename
            entry_name = sound.filename[:-4]
        
        # Save sounds
        await sound.save("./modules_data/sound_board/" + name)
        await interaction.response.send_message(f"✅ Successfully uploaded {sound.filename} as `{entry_name}`.\nIt will be usable after the next bot restart.")

        self.logger.info(f"{interaction.user.name} has uploaded sound {name} to sound board.")


def load(client):
    client.add_cog(SoundBoard(client))