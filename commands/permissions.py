import sys
from nextcord.ext import commands
from nextcord import ui, Role, SlashOption, Embed, Interaction, ButtonStyle, slash_command

sys.path.append("../NosBot")
import logger as log
import dataManager, access

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()
PERMISSIONS_PER_PAGE = 0

def create_choices(choices) -> dict:
    dictionary = {}
    
    index = 0
    for choice in choices:
        for key in choice.keys():
            dictionary[key] = index
            index += 1

    return dictionary

CHOICES = create_choices(dataManager.load_permissions(None))
ADMIN_ACCOUNTS = []


class PermissionsControls(ui.View):
    def __init__(self, permissions):
        super().__init__()
        self.page = 0
        self.permissions = permissions
    

    @ui.button(label="Previous", style=ButtonStyle.gray)
    async def previous(self, button: ui.Button, interaction: Interaction):
        # Change page
        if self.page > 0:
            self.page -= 1
        else:
            await interaction.response.defer()
            return

        # Update embed
        await interaction.message.edit(embed=create_embed(self.permissions, self.page))
        await interaction.response.defer()


    @ui.button(label="Next", style=ButtonStyle.gray)
    async def next(self, button: ui.Button, interaction: Interaction):
        # Change page
        if self.page < len(self.permissions)-1:
            self.page += 1
        else:
            await interaction.response.defer()
            return

        # Update embed
        await interaction.message.edit(embed=create_embed(self.permissions, self.page))
        await interaction.response.defer()


class Permissions(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")
    

    @commands.Cog.listener()
    async def on_ready(self):
        global ADMIN_ACCOUNTS     
        ADMIN_ACCOUNTS = dataManager.load_config()["admin_accounts"]
    

    @slash_command(guild_ids=TEST_GUILDS, description="Show command permissions.", force_global=PRODUCTION)
    async def permissions(self, interaction: Interaction):
        return


    @permissions.subcommand(description="Show command permissions.")
    async def view(self, interaction: Interaction, show_only_me: bool = False):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: permissions.")
        
        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "View Permissions"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to view permissions.", ephemeral=True)
            return

        permissions = dataManager.load_permissions(interaction.guild_id)

        # Get mentions for roles
        roles = {}

        for role in interaction.guild.roles:
            roles[role.name] = role.mention
        
        # Change role names to role mentions
        mention_permissions = []

        for page in permissions:
            new_page = {}
            for key in page.keys():
                new_page[key] = []

                for role in page[key]:
                    new_page[key].append(roles[role])

            mention_permissions.append(new_page)

        await interaction.response.send_message(embed=create_embed(mention_permissions), view=PermissionsControls(mention_permissions), ephemeral=show_only_me)

    
    @permissions.subcommand(description="Edit command permission.")
    async def edit(self, interaction: Interaction,
        setting: int = SlashOption(choices=CHOICES),
        operation: str = SlashOption(choices=["add", "remove"]),
        role: Role = SlashOption()
        ):
        # Log
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: permission edit " + list(CHOICES.keys())[setting] + " " + operation + " @" + role.name + ".")
        
        # Return if role is bot managed
        if role.is_bot_managed():
            await interaction.response.send_message("🚫 FAILED. You can't add bot roles to command permissions.", ephemeral=True)
            return

        # Load permissions
        permissions = dataManager.load_permissions(interaction.guild_id, False)
        values = list(permissions.values())
        keys = list(permissions.keys())
        
        # Return if role is duplicate
        if operation == "add":
            for r in values[setting]:
                if role.name == r:
                    await interaction.response.send_message("🚫 FAILED. This role already has permission to " + keys[setting] + ".", ephemeral=True)
                    return
    
        # Return if role isn't there
        if operation == "remove" and not role.name in values[setting]:
            await interaction.response.send_message("🚫 FAILED. This role already doesn't have permission to " + keys[setting] + ".", ephemeral=True)
            return

        # Return if user doesn't have permission to edit permissions
        if not access.has_access(interaction.user, interaction.guild, "Edit Permissions"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to edit command permissions.", ephemeral=True)
            return
        
        # Modify command permission
        key = keys[setting]

        if operation == "add":
            permissions[key].append(role.name)
            await interaction.response.send_message("✅ Successfully added permission for " + role.name + " to " + key + ".", ephemeral=True)
        else:
            permissions[key].remove(role.name)
            await interaction.response.send_message("✅ Successfully removed permission for " + role.name + " to " + key + ".", ephemeral=True)
        
        # Save it
        dataManager.save_permissions(interaction.guild_id, permissions)
    
    @permissions.subcommand(description="Reset all command permissions to default.")
    async def reset(self, interaction: Interaction):
        self.logger.log_info(interaction.user.name + "#" + interaction.user.discriminator + " has called command: permissions reset.")

        # Return if user doesn't have permission to edit permissions
        if not access.has_access(interaction.user, interaction.guild, "Edit Permissions"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to reset command permissions.", ephemeral=True)
            return
        
        dataManager.reset_permissions(interaction.guild_id)
        await interaction.response.send_message("✅ Successfully reset command permissions to default.", ephemeral=True)


def create_embed(permissions, page=0) -> Embed:
    # Create embed
    embed: Embed = Embed(title="NosBot Permissions", description="Configure Who Can Use What Commands and Features", color=0xFBCE9D)
    
    # List settings and roles
    for key in permissions[page].keys():
        roles = ""

        for role in permissions[page][key]:
            roles += role + " "

        if roles == "":
            roles = "Owner Only"

        embed.add_field(name=key, value=roles, inline=False)

    embed.add_field(name="Use /permission edit [setting name] [add/remove] [role]", value="Page: " + str(page+1) + "/" + str(len(permissions)), inline=False)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/4lt3rnative/nosbot/main/nosbot.png")

    return embed


def load(client: commands.Bot):
    client.add_cog(Permissions(client))