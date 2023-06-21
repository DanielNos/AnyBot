import logging, os
from typing import Tuple, Dict
from logging import Logger
from nextcord.ext.commands import Cog, Bot
from nextcord import Member, Interaction, slash_command
import config


def check_directory() -> bool:
    if not os.path.exists("./modules_data/welcome_message/"):
        os.mkdir("./modules_data/welcome_message")
        return False
    
    return True


def save_welcome_message(guild_id: int, enabled: bool, message: str) -> bool:
    check_directory()

    try:
        file = open("./modules_data/welcome_message/" + str(guild_id), "w", encoding="utf-8")
        file.write("1\n" if enabled else "0\n")
        file.write(message)
        file.close()
        return True
    except:
        return False


def load_welcome_messages() -> Dict[int, Tuple[bool, str]]:
    if not check_directory():
        return {}

    messages = {}
    for file_name in os.listdir("./modules_data/welcome_message/"):

        file = open("./modules_data/welcome_message/" + file_name, "r")
        lines = file.readlines()
        file.close()

        if len(lines) != 2:
            os.remove("./modules_data/welcome_message/" + file_name)
            continue

        messages[int(file_name)] = (lines[0][0] == "1", lines[1])

    return messages


class WelcomeMessage(Cog):
    def __init__(self, client):
        self.client: Bot = client
        self.logger: Logger = logging.getLogger("bot")
        
        self.messages = load_welcome_messages()
        self.logger.info(f"Loaded {len(self.messages)} welcome messages.")
    

    @slash_command(name="welcome_message", guild_ids=config.DEBUG["test_guilds"])
    async def welcome_message(self, interaction: Interaction):
        pass


    @welcome_message.subcommand(name="set", description="Sets server welcome message.")
    async def set(self, interaction: Interaction, message: str):
        
        # Invalid message
        if len(message) == 0:
            await interaction.response.send_message("❌ Failed. Message is too short.", ephemeral=True)
            return
        
        # Message doesn't contain $user$
        if "$user$" not in message:
            await interaction.response.send_message("❌ Failed. Welcome message has to contain $user$. This will be replaced with user names in the welcome messages.", ephemeral=True)
            return
        
        await interaction.response.defer()

        # Load message
        welcome_message = self.messages.get(interaction.guild_id)

        # Save edited message
        if welcome_message is None:
            if save_welcome_message(interaction.guild_id, True, message):
                self.messages[interaction.guild_id] = (True, message)

            await interaction.followup.send(f"✅ Welcome message was enabled and set to:\n{message}")
        else:
            if save_welcome_message(interaction.guild_id, welcome_message[0], message):
                self.messages[interaction.guild_id] = (welcome_message[0], message)
            
            await interaction.followup.send(f"✅ Welcome message was set to:\n{message}")


    @welcome_message.subcommand(name="enabled", description="Enables/Disables the welcome message.")
    async def enabled(self, interaction: Interaction, enabled: bool):

        # Load message
        message = self.messages.get(interaction.guild_id)

        # Message doesn't exist
        if message is None:
            await interaction.response.send_message("❌ Failed. You have to create a welcome message before enabling/disabling it. Use `/welcome_message set`.", ephemeral=True)
            return
        
        # Save change
        if message[0] != enabled:
            if save_welcome_message(interaction.guild_id, enabled, message[1]):
                self.messages[interaction.guild_id] = (enabled, message[1])
            
        await interaction.response.send_message(f"✅ Changed welcome message to `{ 'enabled' if enabled else 'disabled' }`.")


    @welcome_message.subcommand(name="status", description="Shows information about server welcome message.")
    async def status(self, interaction: Interaction):

        message = self.messages.get(interaction.guild_id)

        if message is None:
            await interaction.response.send_message("There isn't any welcome message set at this server. You can use `/welcome_message set` to set it up.")
            return
        
        await interaction.response.send_message(f"**{interaction.guild.name}'s Welcome Message**\nEnabled: `{'Yes' if message[0] else 'No'}`\nMessage: `{message[1]}`")
    

    Cog.listener()
    async def on_member_join(self, member: Member):
        print("GUILD: " + str(member.guild.id))
        message = self.messages.get(member.guild.id)

        # Return if message doesn't exist, is disabled or guild doesn't have a system channel
        if message is None or not message[0] or member.guild.system_channel is None:
            return
        
        await member.guild.system_channel.send(message[1].replace("$user$", member.mentions))


def load(client):
    client.add_cog(WelcomeMessage(client))