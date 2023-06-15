from discord import VoiceClient

class SoundBoardManager:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.voice_client: VoiceClient | None = None
        self.playing: str | None = None
        self.volume: int = 100
        self.messages = []
        self.queue = []


    def queue_str(self) -> str:
        if len(self.queue) == 0:
            return ""

        text = self.queue[0][0]

        for i in range(1, len(self.queue)):
            text += "\n" + self.queue[i][0]
        
        return text