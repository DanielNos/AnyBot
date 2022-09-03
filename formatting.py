from nextcord import User

NUMBERS = { 0: "0️⃣", 1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣" }
LETTERS = { 0: "🇦", 1: "🇧", 2: "🇨", 3: "🇩", 4: "🇪", 5: "🇫", 6: "🇬", 7: "🇭", 8: "🇮", 9: "🇯", 10: "🇰", 11: "🇱", 12: "🇲", 13: "🇳", 14: "🇴", 15: "🇵", 16: "🇶", 17: "🇷", 18: "🇸", 19: "🇹", 20: "🇺", 21: "🇻", 22: "🇼", 23: "🇽", 24: "🇾", 25: "🇿" }

def complete_name(user: User) -> str:
    return user.name + "#" + user.discriminator

def letter_to_emoji(letter: str) -> str:
    index = "abcdefghijklmnopqrstuvwxyz".index(letter[0].lower())
    return LETTERS[index]