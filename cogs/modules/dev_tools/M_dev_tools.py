from logging import Logger, getLogger
from nextcord.ext.commands import Cog, Bot, Context, command
from config import AUTHOR


async def can_use(ctx: Context):
    if ctx.author.id != AUTHOR["id"]:
        await ctx.reply("❌ You don't have rights! 😅")
        return False
    
    return True


class DevTools(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = getLogger("bot")


    @command()
    async def eval(self, ctx: Context, expression: str = None):
        
        # Only bot author can use
        if not await can_use(ctx):
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
        if not await can_use(ctx):
            return

        msg: str = ""
        for cog in self.client.cogs:
            msg += cog + "\n"

        await ctx.reply(msg)

    
def load(client):
    client.add_cog(DevTools(client))