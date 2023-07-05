from nextcord import InteractionMessage, Role
from typing import Dict


class RoleGiver:
    def __init__(self, roles: Dict[str, Role]):
        self.roles = roles
    

class RoleGiverBlueprint:
    def __init__(self):
        self.message: InteractionMessage = None
        self.roles = []
    

    def add_role(self, role: Role, label: str, emoji: str | None = None):
        self.roles.append((role, label, emoji))