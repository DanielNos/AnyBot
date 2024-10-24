from logging import Logger, getLogger
from nextcord.ext.commands import Cog, Bot, Context, command
from config import AUTHOR


class DevTools(Cog):
    def __init__(self, client: Bot):
        self.client: Bot = client
        self.logger: Logger = getLogger("bot")


    @command()
    async def eval(self, ctx: Context, expression: str = None):
        
        # Only bot author can use
        if ctx.author.id != AUTHOR["id"]:
            return

        # No expression
        if expression is None:
            await ctx.reply("No expression provided. Use `eval [expression]`.")
            return

        self.logger.info(f"Evaluating expression: {expression}")
        eval(expression)
    

    @command()
    async def list_cogs(self, ctx: Context):
        
        # Only bot author can use
        if ctx.author.id != AUTHOR["id"]:
            return

        # Collect cog names
        cogs = [cog for cog in self.client.cogs]

        # Get max length of cog name
        max_len = 0
        for cog in cogs:
            if len(cog) > max_len:
                max_len = len(cog)

        max_len += 1

        # Construct message
        msg: str = "Currently loaded:\n```"
        column = 0

        for cog in cogs:
            msg += cog + " " * (max_len - len(cog))

            if column > 3:
                column = 0
                msg += "\n"

        await ctx.reply(msg + "```")


def load(client):
    client.add_cog(DevTools(client))
