import nextcord, dataManager, sys
from nextcord.ext import commands
sys.path.append("./commands/")
import roleGiver, help

# Global variables
CONFIG = dataManager.load_config()

# Set intents
intents = nextcord.Intents.default()
intents.guild_messages = True
intents.message_content = True
intents.guild_reactions = True

client = commands.Bot(command_prefix="?", intents=intents)

# Load commands
roleGiver.load(client)
help.load(client)

print("Commands loaded.\nLoading command data...")
client.run(CONFIG["token"])