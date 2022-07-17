import logger as log
import nextcord, dataManager, sys
from nextcord.ext import commands
sys.path.append("./commands/")
import roleGivers, help, clear, info, utilities, polls

# Global variables
CONFIG = dataManager.load_config()

# Set intents
intents = nextcord.Intents.default()
intents.guild_messages = True
intents.message_content = True
intents.guild_reactions = True

client = commands.Bot(command_prefix="?", intents=intents)

# Load commands
roleGivers.load(client)
help.load(client)
clear.load(client)
info.load(client)
utilities.load(client)
polls.load(client)

logger = log.Logger("./logs/log.txt")

logger.log_info("Commands loaded.")
logger.log_info("Loading command data...")

client.run(CONFIG["token"])