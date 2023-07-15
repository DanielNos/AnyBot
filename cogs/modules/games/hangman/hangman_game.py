from typing import Dict
from nextcord import User, Message, Embed
from formatting import LETTERS, LETTERS_TO_EMOJIS
from config import BOT


ALLOWED_CHARS = "&:-' "


class Game:
    def __init__(self, creator: User, expression: str, game_messages: Dict[int, int], users_in_games: Dict):
        self.message: Message = None
        self.creator: User = creator
        self.expression: str = expression.upper()

        self.players = []
        self.letters = [False] * len(LETTERS)
        self.wrong_guesses = 0

        self.game_messages = game_messages
        self.users_in_games = users_in_games
    

    def create_embed(self) -> Embed:
        embed: Embed = Embed(title="Hangman", color=BOT["color"])

        # Expression
        expression = "```\n"
        for i in range(len(self.expression)):
            if self.expression[i] in ALLOWED_CHARS:
                expression += self.expression[i] + " "
            else:
                if not self.letters[LETTERS.index(self.expression[i].lower())]:
                    expression += "_ "
                else:
                    expression += self.expression[i] + " "

        embed.add_field(name="Expression:", value=expression[:-1] + "\n```", inline=False)

        # Letters
        letters = ""
        for i in range(len(LETTERS)):
            if not self.letters[i]:
                letters += LETTERS_TO_EMOJIS[i] + " "
            else:
                letters += LETTERS[i].upper() + " "

        embed.add_field(name="Letters:", value=letters[:-1], inline=False)

        # Players
        players = ""
        for player in self.players:
            players += player.mention + " "
        
        if players == "":
            players = "none "

        embed.add_field(name="Players:", value=players[:-1], inline=False)

        # Icon
        embed.set_thumbnail(f"https://raw.githubusercontent.com/4lt3rnative/nosbot/main/hangman{self.wrong_guesses}.png")

        # Creator
        embed.set_footer(text=f"Creator: {self.creator.name}")
        
        return embed
    

    def delete(self):
        for player in self.players:
            self.users_in_games.pop(player.id)
        
        if self.message.id in self.game_messages.keys():
            self.game_messages.pop(self.message.id)
        if self.message.id in self.users_in_games.keys():
            self.users_in_games.pop(self.creator.id)
    
    
    def check_for_victory(self) -> bool:
        # Get all the correctly guessed letters
        used_letters = ""
        for i in range(len(LETTERS)):
            if self.letters[i]:
                used_letters += LETTERS[i]
        
        # Try to recreate expression with guessed letters
        complete_expression = ""
        for letter in self.expression.lower():
            if letter in used_letters or letter in ALLOWED_CHARS:
                complete_expression += letter
        
        return complete_expression == self.expression.lower()