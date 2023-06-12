from discord import VoiceClient

class SoundBoardManager:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.voice_client: VoiceClient | None = None
        self.playing: str | None = None
        self.volume: int = 100
        self.messages = []
