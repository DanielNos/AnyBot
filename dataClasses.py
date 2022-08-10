class Poll():
    def __init__(self, emojis, can_change_votes: bool, voted = []):
        self.emojis = emojis
        self.can_change_votes = can_change_votes
        self.voted = voted
    
    
    def to_json(self) -> dict:
        return {
            "emojis": self.emojis,
            "can_change_votes": self.can_change_votes,
            "voted": self.voted
        }


class RoleGiver():
    def __init__(self, message_id: int, role_ids = []):
        self.message_id = message_id
        self.role_ids = role_ids
    
    def to_json(self):
        return {
            "message_id": self.message_id,
            "role_ids": self.role_ids
        }
    
    def __str__(self):
        return "RoleGiver{message_id=" + str(self.message_id) + ", role_ids=" + str(self.role_ids) + "}"