import os, nextcord, logging, asyncio
from importlib import import_module
from nextcord.ext.commands import Bot
from logging.config import dictConfig
import config


async def load_cogs_from_directory(client: Bot, logger: logging.Logger, directory: str):

    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:

            if filename.endswith(".py") and filename.startswith("M_"):

                cog_name = os.path.splitext(filename)[0][2:]
                module_path = os.path.join(dirpath, filename)
                package_path = os.path.relpath(module_path).replace(os.path.sep, '.')[:-3]
                
                # Load module
                module = import_module(package_path)
                module.load(client)
                logger.info(f"Loaded cog: {cog_name}")


async def load_cogs(client: Bot):
    # Setup logger
    logger: logging.Logger = logging.getLogger("bot")
    logger.info("Loading cogs.")

    # Check if files exist
    for dir in ["./cogs/", "./cogs/core", "./cogs/modules", "./modules_data"]:
        if not os.path.exists(dir):
            os.mkdir(dir)
    
    for name in ["core"]:
        if not os.path.exists("./cogs/core/" + name +".py"):
            logger.critical(f"Missing \"{name}\" cog in cogs/core directory. Can't start without \"{name}\" cog.")
            exit(1)

    # Load core
    import cogs.core.core
    cogs.core.core.load(client)
    logger.info(f"Loaded cog: core")

    # Load modules
    await load_cogs_from_directory(client, logger, "./cogs/modules/")


if __name__ == "__main__":
    # Collect token
    token = os.getenv("NOSBOT_DISCORD_API_TOKEN")
    if token == None:
        print("No Discord API token set. Assign your API token to the NOSBOT_DISCORD_API_TOKEN enviroment variable.")
        exit(1)

    # Setup logger
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")
    dictConfig(config.LOGGING_CONFIG)

    # Start client
    client: Bot = Bot(command_prefix="ž", intents=nextcord.Intents.all())

    asyncio.run(load_cogs(client))

    client.run(token)