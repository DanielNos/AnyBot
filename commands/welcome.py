import nextcord, sys
from nextcord.ext import commands
from nextcord import slash_command, Interaction, Member

sys.path.append("../NosBot")
import  dataManager, access
import logger as log

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()
logger = None


class Welcome(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        global logger
        logger = log.Logger("./logs/log.txt")


    @slash_command(guild_ids=TEST_GUILDS, description="Welcome!", force_global=PRODUCTION)
    async def welcome_message(self, interaction: Interaction):
        return
    

    @welcome_message.subcommand(description="Show current welcome message.")
    async def show(self, interaction: Interaction):
        logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: welcome_message show.")

        # Return if user doesn't have access to this command
        if not access.has_access(interaction.user, interaction.guild, "Manage Welcome Message"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission view the welcome message.", ephemeral=True)
            return

        # Load message
        message = dataManager.load_welcome_message(interaction.guild_id)

        if not message:
            message = "ℹ️ There currently isn't any welcome message on this server. Use welcome_message set [message] to set one."
        else:
            message = "ℹ️ This server's message is: \"" + message + "\""

        await interaction.response.send_message(content=message, ephemeral=True)


    @welcome_message.subcommand(description="Set the welcome message.")
    async def set(self, interaction: Interaction, message: str):
        logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: welcome_message set \"" + message + "\".")

        # Return if user doesn't have access to this command
        if not access.has_access(interaction.user, interaction.guild, "Manage Welcome Message"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission set the welcome message.", ephemeral=True)
            return

        # Return if message is empty
        if message.strip() == "":
            await interaction.response.send_message("🚫 FAILED. Welcome message can't be empty. If you want to remove it use welcome_message remove.", ephemeral=True)
            return
        
        # Return if message doesn't contain [user] mention
        if not "[user]" in message:
            await interaction.response.send_message("🚫 FAILED. Your message doesn't contain the \"[user]\" tag. It will be replaced with the user mention. Message example: \"Hello [user], welcome to our server!\"", ephemeral=True)
            return

        # Set the message
        dataManager.save_welcome_message(interaction.guild_id, message)
        await interaction.response.send_message("✅ Successfully changed welcome message to \"" + message + "\".\nNote that welcome messages won't be send if your server doesn't have a system channel selected in the server settings.", ephemeral=True)
    

    @welcome_message.subcommand(description="Remove the welcome message.")
    async def remove(self, interaction: Interaction):
        logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: welcome_message remove.")

        # Return if user doesn't have access to this command
        if not access.has_access(interaction.user, interaction.guild_id, "Manage Welcome Message"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission remove the welcome message.", ephemeral=True)
            return
        
        # Remove the message
        dataManager.remove_welcome_message(interaction.guild_id)
        await interaction.response.send_message("✅ Successfully removed the welcome message.")


    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        logger.log_info(member.name + "#" + member.discriminator + " has joined guild " + member.guild.name + ".")

        guild = member.guild

        # Return if guild doesn't have a system channel
        if guild.system_channel is None:
            return

        # Return if guild doesn't have a welcome message
        message = dataManager.load_welcome_message(member.guild.id)
        if not message:
            return

        # Send the message
        await guild.system_channel.send(message.replace("[user]", member.mention))


def load(client: commands.Bot):
    client.add_cog(Welcome(client))