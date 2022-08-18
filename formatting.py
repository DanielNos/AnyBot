from nextcord import User

def complete_name(user: User) -> str:
    return user.name + "#" + user.discriminator