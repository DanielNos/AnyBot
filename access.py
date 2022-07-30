from nextcord import Guild, Member
import dataManager

def has_access(user: Member, guild: Guild, permission: str) -> bool:
    permissions = dataManager.load_permissions(guild.id, False)

    for role in user.roles:
        if role.name in permissions[permission]:
            return True
    
    admins = dataManager.load_config()["admin_accounts"]

    return user.id in admins or user.id == guild.owner_id