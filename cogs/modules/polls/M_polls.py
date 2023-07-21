import os, sys
sys.path.append(os.path.dirname(__file__))

from typing import Dict
from logging import Logger, getLogger
from nextcord.ext.commands import Bot, Cog 
from nextcord import slash_command, Color, RawBulkMessageDeleteEvent, PartialInteractionMessage, Message, User, Embed, Interaction, Reaction, RawMessageDeleteEvent, RawReactionActionEvent
from config import DEBUG
from polls_poll import Poll, progress_bar, save_polls, load_polls
from polls_view import PollDesignerView


class Polls(Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.logger: Logger = getLogger("bot")
        
        self.locked_polls = []
        self.polls: Dict = load_polls()
        self.logger.info(f"Polls module loaded {len(self.polls)} polls.")


    @slash_command(guild_ids=DEBUG["test_guilds"], description="Create a poll.")
    async def poll(self, interaction: Interaction):
        return
    

    @poll.subcommand(description="Create a poll.")
    async def create(self, interaction: Interaction, question: str):

        self.logger.info(f"{interaction.user.name} has created a poll with question: {question}")

        # Send message
        embed: Embed = Embed(title=question, color=Color.random())
        partial_message: PartialInteractionMessage = await interaction.response.send_message(embed=embed)
        message: Message = await partial_message.fetch()

        view = PollDesignerView(self.polls)
        embed.set_footer(text=f"ID: {message.id}\nVote using reactions!")

        await message.edit(embed=embed, view=view)

    

    @poll.subcommand(description="Locks a poll so users won't be able to vote anymore.")
    async def lock(self, interaction: Interaction, poll_id: str):

        # Return if poll doesn't exist
        if poll_id not in self.polls:
            await interaction.response.send_message(f"🚫 Poll with ID {poll_id} wasn't found.", ephemeral=True)
            return
        
        # Lock it
        poll = self.polls.pop(poll)
        save_polls(self.polls)

        self.logger.info(f"{interaction.user.name} has locked poll {poll_id}.")

        await interaction.response.send_message("✅ Successfully locked poll.", ephemeral=True)
    

    @Cog.listener()
    async def on_raw_reaction_add(self, event: RawReactionActionEvent):
        # Cancel if there are no polls
        if len(self.polls) == 0:
            return
            
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
        has_reactions = False
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
        if event.user_id not in self.polls[event.message_id]:
            self.polls[event.message_id].voted.append(event.user_id)

        await self.update_poll(message)


    @Cog.listener()
    async def on_raw_reaction_remove(self, event: RawReactionActionEvent):
        # Cancel if there are no polls
        if len(self.polls) == 0:
            return
        
        # Cancel if message isn't a poll
        if event.message_id not in self.polls:
            return
        
        # Cancel if poll doesn't allow changing votes
        poll: Poll = self.polls[event.message_id]
        if not poll.can_change_votes:
            return

        # Update poll
        if event.user_id in self.polls[event.message_id]:
            self.polls[event.message_id].voted.remove(event.user_id)

        message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)
        await self.update_poll(message)


    @Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in list(self.polls.keys()):
            # Log
            self.logger.info(f"Poll {event.message_id} message was deleted. Removing poll object.")

            # Remove from lists
            self.polls.pop(event.message_id)

            # Save them
            save_polls(self.polls)

    
    @Cog.listener()
    async def on_raw_bulk_message_delete(self, event: RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in list(self.polls.keys()):
                # Log
                self.logger.info(f"Poll {id} message was deleted. Removing poll object.")
                
                # Remove from lists
                self.polls.pop(id)
                
                # Save them
                save_polls(self.polls)


    async def update_poll(self, message: Message):
        embed: Embed = message.embeds[0]
        new_embed: Embed = Embed(title=embed.title, color=embed.color)
        new_embed.set_footer(text=embed.footer.text)

        # Return if reactions are being added by bot
        if len(message.reactions) != len(embed.fields):
            return

        # Get total reaction count
        unique_users = []
        reaction_count = 0
        for reaction in message.reactions:
            reaction_count += reaction.count - 1
        
        # Update bars
        for i in range(len(embed.fields)):
            new_embed.add_field(name=embed.fields[i].name, value=progress_bar(message.reactions[i].count-1, reaction_count), inline=False)
        
        await message.edit(embed=new_embed)


def load(client: Bot):
    client.add_cog(Polls(client))