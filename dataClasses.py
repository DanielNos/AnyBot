class Poll():
    def __init__(self, emojis=[], can_change_votes=True, voted=[]):
        self.emojis = emojis
        self.can_change_votes = can_change_votes
        self.voted = voted
    
    
    def to_json(self) -> dict:
        return {
            "emojis": self.emojis,
            "can_change_votes": self.can_change_votes,
            "voted": self.voted
        }