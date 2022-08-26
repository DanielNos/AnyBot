import logger as log
import nextcord, dataManager
from nextcord.ext import commands
import dataManager


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
logger.log_info("Loading commands...")

dataManager.import_commands("./commands/", client)

logger.log_info("Commands loaded.")


# Run bot
client.run(CONFIG["token"])