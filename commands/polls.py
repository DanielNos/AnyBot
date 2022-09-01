import sys, nextcord, discord_emoji
from random import randint
from nextcord.ui import View, Modal, Button, TextInput
from nextcord.ext import commands
from nextcord import slash_command, ButtonStyle, Message, User, Embed, Interaction, Reaction, RawMessageDeleteEvent

sys.path.append("../NosBot")
import logger as log
import dataManager, formatting, access
from dataClasses import Poll

TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()

polls = {}
poll_ids = {}


class AddOption(Modal):
    def __init__(self, logger: log.Logger, view: View):
        super().__init__(title="Add Option")
        self.logger = logger
        self.view = view

        # Add inputs
        self.option = TextInput(label="Option Text:", min_length=1, max_length=50, required=True)
        self.add_item(self.option)

        self.emoji = TextInput(label="Reaction Emoji:", min_length=1, max_length=50, required=False, placeholder="Optional. Use ':emoji:' format.")
        self.add_item(self.emoji)


    async def callback(self, interaction: Interaction):
        emoji = self.emoji.value.lower()

        # Try to extract emoji from option
        uni_emoji = discord_emoji.to_uni(emoji)
        # Use letter if emoji couldn't be found
        if not uni_emoji:
            uni_emoji = formatting.LETTERS[len(self.view.poll.emojis)]
        
        self.view.poll.emojis.append(uni_emoji)

        # Add option to message
        embed: Embed = interaction.message.embeds[0]
        embed.add_field(name=uni_emoji + " " + self.option.value, value=progress_bar(), inline=False)

        # Enable completing
        self.view.children[3].disabled = False

        await interaction.response.edit_message(embed=embed, view=self.view)


class PollDesigner(View):
    def __init__(self, logger: log.Logger, poll_id: int, enable_complete=False):
        super().__init__()
        self.logger = logger
        self.poll_id = poll_id
        self.poll = Poll()

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
        await interaction.response.send_modal(AddOption(self.logger, self))
    

    async def change_voting(self, interaction: Interaction):
        self.poll.can_change_votes = not self.poll.can_change_votes
        self.children[1].label = "Changing Votes: " + (self.poll.can_change_votes * "Enabled") + ("Disabled" * (not self.poll.can_change_votes))
        
        await interaction.response.edit_message(view=self)


    async def delete(self, interaction: Interaction):
        await interaction.message.delete()
    

    async def complete(self, interaction: Interaction):
        global polls, poll_ids
        polls[interaction.message.id] = self.poll
        poll_ids[self.poll_id] = interaction.message.id

        # Remove controls and add reactions
        message: Message = await interaction.response.edit_message(view=None)
        for emoji in self.poll.emojis:
            await message.add_reaction(emoji)

        # Save polls to file
        dataManager.save_polls(polls, poll_ids)


class Polls(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = log.Logger("./logs/log.txt")


    @commands.Cog.listener()
    async def on_ready(self):
        global polls, poll_ids
        polls, poll_ids = dataManager.load_polls()


    @slash_command(guild_ids=TEST_GUILDS, description="Create a poll.", force_global=PRODUCTION)
    async def poll(self, interaction: Interaction):
        return
    

    @poll.subcommand(description="Create a poll.")
    async def create(self, interaction: Interaction, question: str):
        # Log
        self.logger.log_info(formatting.complete_name(interaction.user) + " has called command: poll create " + question + ".")

        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Manage Polls"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to create polls.", ephemeral=True)
            return

        # Create embed
        poll_id = generate_id()
        embed: Embed = Embed(title=question, color=nextcord.Color.random())
        embed.set_footer(text="ID: " + poll_id + "\nVote using reactions!")

        # Send message
        await interaction.response.send_message(embed=embed, view=PollDesigner(self.logger, poll_id))
    

    @poll.subcommand(description="Locks a poll so users won't be able to vote anymore.")
    async def lock(self, interaction: Interaction, poll_id: str):
        # Log
        self.logger.log_info(formatting.complete_name(interaction.user) + " has called command: lock_poll " + poll_id + ".")

        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Manage Polls"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to lock polls.", ephemeral=True)
            return
            
        # Return if poll doesn't exist
        if not poll_id in poll_ids.keys():
            await interaction.response.send_message("🚫 FAILED. Poll with ID " + poll_id +" wasn't found.", ephemeral=True)
            return
            
        # Lock it
        poll = poll_ids.pop(poll_id)
        polls.pop(poll)

        dataManager.save_polls(polls, poll_ids)
        await interaction.response.send_message("✅ Successfully locked poll.", ephemeral=True)
    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: nextcord.RawReactionActionEvent):
        # Cancel if there are no polls
        if len(polls) == 0:
            return
            
        # Cancel if message isn't a poll
        if not event.message_id in polls.keys():
            return
        
        # Cancel if reaction author is bot
        if event.user_id == self.client.user.id:
            return

        # Remove reaction if it isn't valid
        message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)
        poll: Poll = polls[event.message_id]

        if event.user_id != self.client.user.id and not event.emoji.name in poll.emojis:
            for reaction in message.reactions:
                if str(reaction.emoji) == str(event.emoji.name):
                    await message.remove_reaction(emoji=reaction, member=event.member)
                    return
            return
        
        # Remove reaction if user already voted and changing votes isn't allowed
        if not poll.can_change_votes and event.user_id in poll.voted:
            for reaction in message.reactions:
                if str(reaction.emoji) == str(event.emoji.name):
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
        
        if has_reactions and new_reaction != None:
            await new_reaction.remove(new_user)
            return
        
        # Update poll
        polls[event.message_id].voted.append(event.user_id)
        await self.update_poll(message)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, event: nextcord.RawReactionActionEvent):
        # Cancel if there are no polls
        if len(polls) == 0:
            return
        
        # Cancel if message isn't a poll
        if not event.message_id in polls.keys():
            return
        
        # Cancel if reaction is removed by bot
        if event.user_id == self.client.user.id:
            return
        
        # Cancel if poll doesn't allow changing votes
        poll: Poll = polls[event.message_id]
        if not poll.can_change_votes:
            return

        # Update poll
        message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)
        await self.update_poll(message)


    @commands.Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in list(polls.keys()):
            # Log
            self.logger.log_info("Poll " + str(event.message_id) + " message was deleted. Removing poll object.")

            # Remove from lists
            polls.pop(event.message_id)
            values = list(self.poll_ids.values())
            for i in range(len(values)):
                if values[i] == event.message_id:
                    self.poll_ids.pop(list(self.poll_ids.keys())[i])
                    break

            # Save them
            dataManager.save_polls(polls, self.poll_ids)

    
    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, event: nextcord.RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in list(polls.keys()):
                # Log
                self.logger.log_info("Poll " + str(id) + " message was deleted. Removing poll object.")
                
                # Remove from lists
                polls.pop(id)
                values = list(self.poll_ids.values())
                for i in range(len(values)):
                    if values[i] == id:
                        self.poll_ids.pop(list(self.poll_ids.keys())[i])
                        break
                
                # Save them
                dataManager.save_polls(polls, self.poll_ids)


    async def update_poll(self, message: Message):
        embed: Embed = message.embeds[0]
        new_embed: Embed = Embed(title=embed.title, color=embed.color)
        new_embed.set_footer(text=embed.footer.text)

        # Return if reactions are being added by bot
        if len(message.reactions) != len(embed.fields):
            return

        # Get total reaction count
        reaction_count = 0
        for reaction in message.reactions:
            reaction_count += reaction.count - 1
        
        # Update bars
        for i in range(len(embed.fields)):
            new_embed.add_field(name=embed.fields[i].name, value=progress_bar(message.reactions[i].count-1, reaction_count), inline=False)
        
        await message.edit(embed=new_embed)


def progress_bar(value: float = 0, max: float = 0) -> str:
    if max == 0 or value == 0:
        return "`" + (" " * 30)  +"` | 0% (0)"

    percentage = round((value / max) * 30)

    bar = "`" + ("█" * percentage) + (" " * (30 - percentage)) + "`"

    bar += " | " + str(round((value / max) * 1000) / 10) + "% (" + str(value) + ")"

    return bar


def generate_id() -> str:
    characters = "0123456789abcdefghijklmnopqrstuvwxyz"
    id = ""
    for i in range(10):
        id += characters[randint(0, len(characters)-1)]
    return id


def load(client: commands.Bot):
    client.add_cog(Polls(client))