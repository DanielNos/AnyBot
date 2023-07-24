from logging import Logger, getLogger
from nextcord.ui import View, Button
from nextcord import ButtonStyle, Interaction, Message
from polls_modal import AddOptionModal
from polls_poll import Poll, save_poll
from formatting import get_place


class PollDesignerView(View):
    def __init__(self, polls, enable_complete: bool = False):
        super().__init__()
        self.logger: Logger = getLogger("bot")
        
        self.poll = Poll([], True, [])
        self.polls = polls

        # Create buttons
        button: Button = Button(style=ButtonStyle.blurple, label="Add Option")
        button.callback = self.add_option
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.gray, label="Changing Votes: Enabled")
        button.callback = self.change_voting
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.red, label="Delete")
        button.callback = self.delete
        self.add_item(button)

        button: Button = Button(style=ButtonStyle.green, label="Complete", disabled=(not enable_complete))
        button.callback = self.complete
        self.add_item(button)
    

    async def add_option(self, interaction: Interaction):
        await interaction.response.send_modal(AddOptionModal(self))
    

    async def change_voting(self, interaction: Interaction):
        self.poll.can_change_votes = not self.poll.can_change_votes
        self.children[1].label = f"Changing Votes: {'Enabled' if self.poll.can_change_votes else 'Disbaled'}"
        
        await interaction.response.edit_message(view=self)


    async def delete(self, interaction: Interaction):
        await interaction.message.delete()
    

    async def complete(self, interaction: Interaction):
        self.polls[interaction.message.id] = self.poll

        # Remove controls and add reactions
        message: Message = await interaction.response.edit_message(view=None)
        for emoji in self.poll.emojis:
            await message.add_reaction(emoji)

        for i in self.poll.emojis:
            self.poll.voted.append(set())

        # Save polls to file
        save_poll(interaction.message.id, self.poll)
        self.logger.info(f"{interaction.user.name} has completed a poll {interaction.message.id} in {get_place(interaction)}.")