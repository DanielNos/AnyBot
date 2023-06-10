import os, discord, asyncio, logging
from discord.ext import commands
from logging.config import dictConfig

import config


async def load_cogs(client: commands.Bot):
    logger: logging.Logger = logging.getLogger("bot")
    logger.info("Loading cogs.")

    for file in os.listdir("./cogs"):
        if not file.endswith(".py"):
            continue

        await client.load_extension("cogs." + file[:-3])
        logger.info(f"Loaded cog: {file[:-3]}")



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
    client: commands.Bot = commands.Bot(command_prefix="NOPE", intents=discord.Intents.all())

    asyncio.run(load_cogs(client))

    client.run("OTkwMjc2MzEzMjg3ODg4ODk2.GOG5Hv.oSS-XAI76g6In4Qp5R0LSms7zqqpqLRPZ5ojLo", root_logger=True)