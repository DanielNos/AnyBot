import logger as log
import nextcord, dataManager, sys
from nextcord.ext import commands

sys.path.append("./commands/")
import roleGivers, help, clear, info, utilities, polls, permissions, welcome

sys.path.append("./commands/games/")
import tictactoe, hangman

# Setup logger
logger = log.Logger("./logs/log.txt")

# Global variables
CONFIG = dataManager.load_config()
logger.log_info("Config loaded.")

# Set intents
intents = nextcord.Intents.default()
intents.guild_messages = True
intents.message_content = True
intents.guild_reactions = True
intents.members = True

client = commands.Bot(command_prefix="?", intents=intents)

# Load commands
roleGivers.load(client)
help.load(client)
clear.load(client)
info.load(client)
utilities.load(client)
polls.load(client)
permissions.load(client)
welcome.load(client)

# Load Games
tictactoe.load(client)
hangman.load(client)

logger.log_info("Commands loaded.")
logger.log_info("Loading commands data...")

# Run bot
client.run(CONFIG["token"])