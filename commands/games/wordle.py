import sys
from nextcord.ext import commands
from nextcord import PartialInteractionMessage, Message, Embed, ButtonStyle, Interaction, slash_command
from nextcord.ui import View, Button, Modal, TextInput
from random import sample

sys.path.append("../NosBot")
import logger as log
import dataManager
from formatting import complete_name, letter_to_emoji

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

WORDS = dataManager.load_wordle_words()

games = {}


class Game():
    def __init__(self):
        self.words = [""] * 6
        self.correct = sample(WORDS, 1)[0]
        self.turn = 0
        print(self.correct)
    

    def create_embed(self) -> Embed:
        embed: Embed = Embed(title="Wordle")
        embed.set_thumbnail("https://raw.githubusercontent.com/4lt3rnative/nosbot/main/wordle.png")

        rows = ""
        for i in range(6):
            # Create word
            if len(self.words[i]) == 5:
                for char in self.words[i]:
                    rows += letter_to_emoji(char) + " "
            else:
                rows += "⬛ " * 5

            # Create indicators
            rows += "\n"

            for j in range(5):
                if j < len(self.words[i]):
                    if self.words[i][j] == self.correct[j]:
                        rows += "🟩 "
                    elif self.words[i][j] in self.correct:
                        rows += "🟨 "
                    else:
                        rows += "⬜ "
                else:
                    rows += "🔳 "

            rows += "\n"

        turn = self.turn + 1 * int(self.victory() != True)
        if turn > 6:
            turn = 6

        embed.add_field(name="Turn: " + str(turn) + "/6", value=rows)

        return embed
    

    def victory(self) -> bool:
        if self.words[self.turn-1] == self.correct:
            return True
        elif self.turn-1 == 5:
            return False
        return None


class WordInput(Modal):
    def __init__(self):
        super().__init__(title="Guess Word")

        self.text_input = TextInput(label="Enter a valid 5 letter word:", required=True, min_length=5, max_length=5)
        self.add_item(self.text_input)

    
    async def callback(self, interaction: Interaction):
        word = self.text_input.value.lower()

        # Return if word isn't valid
        if len(word) != 5 or word not in WORDS:
            await interaction.response.defer()
            return

        game: Game = games[interaction.message.id]

        game.words[game.turn] = word
        game.turn += 1

        embed = game.create_embed()
        view = True

        # Check for victory and defeat
        victory = game.victory()
        if victory is not None:
            view = False
            games.pop(interaction.message.id)
            dataManager.add_game_record(interaction.user.id, "wordle", victory)

            if victory:
                embed.add_field(name="🎉 You won! 🎉", value="Congratulations!", inline=False)
            else:
                embed.add_field(name="💢 You lost! 💢", value="Better luck next time!", inline=False)
        
        # Edit message
        if view:
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.edit_message(embed=embed, view=None)


class Controls(View):
    def __init__(self):
        super().__init__()

        # Create buttons
        button: Button = Button(label="Guess Word", style=ButtonStyle.gray)
        button.callback = self.guess_word
        self.add_item(button)

        button: Button = Button(label="Quit", style=ButtonStyle.red)
        button.callback = self.quit
        self.add_item(button)

    
    async def guess_word(self, interaction: Interaction):
        await interaction.response.send_modal(WordInput())
    

    async def quit(self, interaction: Interaction):
        self.children = []
        games.pop(interaction.message.id)

        await interaction.response.send_message(embed=interaction.message.embeds[0], view=self)


class Wordle(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @slash_command(guild_ids=TEST_GUILDS, description="Start a game of Wordle.", force_global=PRODUCTION)
    async def wordle(self, interaction: Interaction):
        self.logger.log_info(complete_name(interaction.user) + " has called command: wordle.")

        game: Game = Game()
        
        partial_message: PartialInteractionMessage = await interaction.response.send_message(embed=game.create_embed(), view=Controls(), ephemeral=True)
        message: Message = await partial_message.fetch()

        games[message.id] = game


def load(client: commands.Bot):
    client.add_cog(Wordle(client))