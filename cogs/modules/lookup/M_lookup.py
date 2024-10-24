from logging import Logger, getLogger
from nextcord.ext.commands import Cog, Bot
from nextcord import Guild, TextChannel, VoiceChannel, User, Interaction, SlashOption, slash_command
from config import DEBUG


class Lookup(Cog):
    def __init__(self, client: Bot):
        self.client: Bot = client
        self.logger: Logger = getLogger("bot")


    @slash_command(description="Finds target using Disccord API by it's ID.", guild_ids=DEBUG["test_guilds"])
    async def lookup(self, interaction: Interaction, target: str = SlashOption(choices=["Guild", "Channel", "Message", "User"]), id: str = SlashOption(required=True)):

        if interaction.user.id != 277796227397976064:
            await interaction.response.send_message("❌ You don't have rights! 😅", ephemeral=True)
            return

        id = int(id)
        
        if target == "Guild":
            # Fetch guild
            try:
                guild: Guild = await self.client.fetch_guild(id)
            except:
                await interaction.response.send_message("❌ Failed to fetch.", ephemeral=True)
                return
            
            # Fetch owner
            try:
                owner: User = await self.client.fetch_user(guild.owner_id)
            except:
                owner = None
            
            await interaction.response.send_message(f"```Target: GUILD\nName: {guild.name}\nDescription:{guild.description}\nRegion: {guild.region}\nMember Count: {guild.member_count}\nAproximate Member Count: {guild.approximate_member_count}\nAproximate Presence Count: {guild.approximate_presence_count}\nOwner: {owner.name} ({guild.owner_id})\nCreated At: {guild.created_at}```", ephemeral=True)
            return
        
        if target == "Channel":
            # Fetch channel
            try:
                channel: TextChannel = await self.client.fetch_channel(id)
            except:
                await interaction.response.send_message("❌ Failed to fetch.", ephemeral=True)
                return
            
            message = f"```Target: CHANNEL\nChannel Type: {str(type(channel))[25:-2]}\nName: {channel.name}\nGuild: {channel.guild}\nNSFW: {channel.is_nsfw()}\n"

            if type(channel) == VoiceChannel:
                message += f"User Limit: {channel.user_limit}\nRTC Region: {channel.rtc_region}"

            await interaction.response.send_message(f"{message}```", ephemeral=True)
            return
        
        if target == "Message":
            # Try to find message in cache
            for message in self.client.cached_messages:
                if message.id == id:
                    attachments = ""
            
                    for attachment in message.attachments:
                        attachments += f"{attachment.filename} : {attachment.url}\n"

                    await interaction.response.send_message(f"```Target: MESSAGE\nGuild:{message.guild.name}\nChannel: {message.channel.name}\nConent: {message.content}\nAuthor: {message.author.name} ({message.author.id})\nAttachments: {attachments}```", ephemeral=True)
                    return
            
            await interaction.response.send_message("❌ Not in cache.", ephemeral=True)
            return
        
        if target == "User":
            # Fetch user
            try:
                user: User = await self.client.fetch_user(id)
            except:
                await interaction.response.send_message("❌ Failed to fetch.", ephemeral=True)
                return
            
            if len(user.mutual_guilds) >= 1:
                mutual_guilds = f"{user.mutual_guilds[0].name} ({user.mutual_guilds[0].id})"

            for i in range(1, len(user.mutual_guilds)):
                mutual_guilds += f", {user.mutual_guilds[i].name} ({user.mutual_guilds[i].id})"
            
            await interaction.response.send_message(f"```Target: USER\nName: {user.name}\nID: {user.id}\nDisplay Name: {user.display_name}\nAvatar: {user.avatar.url}\nBot: {user.bot}\nColor: {user.color}\nAccent Color: {user.accent_color}\nCreated At: {user.created_at}\nMutual Guilds: {mutual_guilds}```", ephemeral=True)
            



def load(client):
    client.add_cog(Lookup(client))
