import os, sys
sys.path.append(os.path.dirname(__file__))

from typing import Dict
from logging import Logger, getLogger
from nextcord.ext.commands import Bot, Cog 
from nextcord import slash_command, Color, RawBulkMessageDeleteEvent, PartialInteractionMessage, Message, User, Embed, Guild, Interaction, Reaction, RawMessageDeleteEvent, RawReactionActionEvent
from config import DEBUG
from polls_poll import Poll, progress_bar, save_polls, load_polls, save_poll
from polls_view import PollDesignerView
from formatting import get_place


class Polls(Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.logger: Logger = getLogger("bot")
        
        self.locked_polls = []
        self.polls: Dict[int, Poll] = load_polls()
        self.logger.info(f"Loaded {len(self.polls)} polls.")


    @slash_command(guild_ids=DEBUG["test_guilds"], description="Create a poll.")
    async def poll(self, interaction: Interaction):
        return
    

    @poll.subcommand(description="Creates a poll.")
    async def create(self, interaction: Interaction, text: str):

        self.logger.info(f"{interaction.user.name} has created a poll with text \"{text}\" in {get_place(interaction)}.")

        # Send message
        embed: Embed = Embed(title=text, color=Color.random())
        partial_message: PartialInteractionMessage = await interaction.response.send_message(embed=embed)
        message: Message = await partial_message.fetch()

        view = PollDesignerView(self.polls)
        embed.set_footer(text=f"ID: {message.id}\nVote using reactions!")

        await message.edit(embed=embed, view=view)


    @poll.subcommand(description="Locks a poll so users won't be able to vote anymore. This can't be reverted!")
    async def lock(self, interaction: Interaction, poll_id: str):

        poll_id = int(poll_id)

        # Return if poll doesn't exist
        if poll_id not in self.polls:
            await interaction.response.send_message(f"🚫 Poll with ID {poll_id} wasn't found.", ephemeral=True)
            return
        
        # Edit message
        try:
            message: Message = await interaction.channel.fetch_message(poll_id)
        except:
            await interaction.response.send_message(f"🚫 Poll with ID {poll_id} isn't in this channel. You have to use `/poll lock` in the same channel as the poll.", ephemeral=True)
            return

        embed: Embed = message.embeds[0]
        embed.set_footer(text="Voting has ended.")

        await message.edit(embed=embed)

        # Lock it
        self.polls.pop(poll_id)
        save_polls(self.polls)


        self.logger.info(f"{interaction.user.name} has locked poll {poll_id}.")

        await interaction.response.send_message("✅ Successfully locked poll.", ephemeral=True)
    

    @Cog.listener()
    async def on_raw_reaction_add(self, event: RawReactionActionEvent):
            
        # Cancel if message isn't a poll
        if event.message_id not in self.polls:
            return
        
        # Cancel if reaction author is bot
        if event.user_id == self.client.user.id:
            return

        # Remove reaction if it isn't valid
        message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)
        poll: Poll = self.polls[event.message_id]

        if event.user_id != self.client.user.id and not event.emoji.name in poll.emojis:
            for reaction in message.reactions:
                if str(reaction.emoji) == event.emoji.name:
                    await message.remove_reaction(emoji=reaction, member=event.member)
                    return
            return
        
        # Remove reaction if user already voted and changing votes isn't allowed
        if not poll.can_change_votes and event.user_id in poll.voted:
            for reaction in message.reactions:
                if str(reaction.emoji) == event.emoji.name:
                    await message.remove_reaction(emoji=reaction, member=event.member)
                    return
            return
        
        # Remove reaction if user already has reacted
        has_reactions: bool = False
        new_reaction: Reaction = None
        new_user: User = None

        for reaction in message.reactions:
            for user in await reaction.users().flatten():
                if user.id == event.user_id:
                    if reaction.emoji != event.emoji.name:
                        has_reactions = True
                    else:
                        new_reaction = reaction
                        new_user = user
        
        if has_reactions and new_reaction is not None:
            await new_reaction.remove(new_user)
            return
        
        # Update poll
        poll: Poll = self.polls[event.message_id]
        option_index = poll.emojis.index(str(event.emoji))

        if event.user_id not in poll.voted[option_index]:
            poll.voted[option_index].add(event.user_id)

        await self.update_poll(message)
        self.logger.info(f"{new_user.name} voted in poll {message.embeds[0].title} ({message.id}) for option {option_index}.")
        save_poll(event.message_id, poll)


    @Cog.listener()
    async def on_raw_reaction_remove(self, event: RawReactionActionEvent):
        
        # Cancel if message isn't a poll
        if event.message_id not in self.polls:
            return
        
        # Cancel if poll doesn't allow changing votes
        poll: Poll = self.polls[event.message_id]
        if not poll.can_change_votes:
            return

        # Update poll
        poll: Poll = self.polls[event.message_id]
        option_index = poll.emojis.index(str(event.emoji))

        if event.user_id in poll.voted[option_index]:
            poll.voted[option_index].remove(event.user_id)

        message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)
        
        await self.update_poll(message)
        self.logger.info(f"{event.user_id} voted in poll {message.embeds[0].title} ({message.id}) for option {option_index}.")
        save_poll(event.message_id, poll)


    @Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):

        if event.message_id in list(self.polls.keys()):
            # Remove from lists
            self.polls.pop(event.message_id)

            # Save them
            save_polls(self.polls)
            self.logger.info(f"Poll {event.message_id} message was deleted. Removing poll object.")

    
    @Cog.listener()
    async def on_raw_bulk_message_delete(self, event: RawBulkMessageDeleteEvent):

        for id in event.message_ids:
            if id in list(self.polls.keys()):
                # Remove from lists
                self.polls.pop(id)
                
                # Save them
                save_polls(self.polls)
                self.logger.info(f"Poll {id} message was deleted. Removing poll object.")


    async def update_poll(self, message: Message):
        embed: Embed = message.embeds[0]
        new_embed: Embed = Embed(title=embed.title, color=embed.color)
        new_embed.set_footer(text=embed.footer.text)

        # Return if reactions are being added by bot
        if len(message.reactions) != len(embed.fields):
            return

        # Find option with highest vote count
        votes = self.polls[message.id].voted
        max = len(votes[0])

        for i in range(1, len(votes)):
            if len(votes[i]) > max:
                max = len(votes[i])
        
        # Update bars
        for i in range(len(embed.fields)):
            new_embed.add_field(name=embed.fields[i].name, value=progress_bar(len(votes[i]), max), inline=False)
        
        await message.edit(embed=new_embed)


def load(client: Bot):
    client.add_cog(Polls(client))