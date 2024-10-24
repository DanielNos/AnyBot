# AnyBot

AnyBot is a modular Discord bot that provides utility functions, moderation tools, games, and more. Each feature is organized into a separate module, referred to as a cog. Cogs can be easily added or removed, allowing for customization of the bot’s functionality.

# How to Setup and Run

1. Clone the repository.
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the evnironment: `source venv/bin/activate`
4. Install the required modules: `pip install -r requirements.txt`
5. Export an environment variable with your Discord bot API token: `export ANYBOT_DISCORD_API_TOKEN=[your token]`
6. Start the bot: `python3 main.py`

# Configuring Bot

All configuration is done using the `config.py` file. You can set there the bot's name, icon and command prefix, as well as logging and debug.

# Edititing Cogs

Every feature of AnyBot has its own cog in the `cogs/modules` directory. You can remove any cog, except for the `core` cog. You can also add any cog in the directory to automatically register it and load on startup.
The bot needs to be restarted on any change.
