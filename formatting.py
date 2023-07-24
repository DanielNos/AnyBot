from nextcord import Interaction


LETTERS = list("abcdefghijklmnopqrstuvwxyz")
LETTERS_TO_EMOJIS = { 0: "🇦", 1: "🇧", 2: "🇨", 3: "🇩", 4: "🇪", 5: "🇫", 6: "🇬", 7: "🇭", 8: "🇮", 9: "🇯", 10: "🇰", 11: "🇱", 12: "🇲", 13: "🇳", 14: "🇴", 15: "🇵", 16: "🇶", 17: "🇷", 18: "🇸", 19: "🇹", 20: "🇺", 21: "🇻", 22: "🇼", 23: "🇽", 24: "🇾", 25: "🇿" }
NUMBERS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣", "🔟"]


def get_place(interaction: Interaction) -> str:
    if interaction.guild is None:
        return "Direct Messages"
    
    return interaction.guild.name + "/" + interaction.channel.name