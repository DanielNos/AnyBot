class RoleGiver:
    def __init__(self):
        self.roles = []
    
    def add_role(self, label: str, emoji: str | None = None):
        self.roles.append((label, emoji))