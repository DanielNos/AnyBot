import sys, nextcord, emoji
from random import randint
from nextcord.ext import commands
from nextcord import slash_command, Message, PartialInteractionMessage, User, Embed, Interaction, Reaction, RawMessageDeleteEvent

sys.path.append("../NosBot")
import logger as log
import dataManager, emojiDict, access


TEST_GUILDS = dataManager.load_test_guilds()
PRODUCTION = dataManager.is_production()


class Polls(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.polls = {}
        self.poll_ids = {}
        self.logger = log.Logger("./logs/log.txt")


    @commands.Cog.listener()
    async def on_ready(self):
        self.polls, self.poll_ids = dataManager.load_polls()


    @slash_command(guild_ids=TEST_GUILDS, description="Create a poll.", force_global=PRODUCTION)
    async def new_poll(self, interaction: Interaction, question: str, 
    option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None, option6: str = None, 
    option7: str = None, option8: str = None, option9: str = None):

        # Remove not used options
        options = [option1, option2, option3, option4, option5, option6, option7, option8, option9]
        while None in options:
            options.remove(None)

        # Log
        self.logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: new_poll " + question + " options: " + str(options) + ".")

        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Manage Polls"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to create polls.", ephemeral=True)
            return

        # Create embed
        poll_id = generate_id()
        embed: Embed = Embed(title=question, color=nextcord.Color.random())
        embed.set_footer(text="ID: " + poll_id + "\nVote using reactions!")

        # Fill embed with options
        i = 0
        emojis = []
        for option in options:
            # Try to extract emoji from option
            if emoji.emoji_count(option[:2]):
                emojis.append(option[:2])
            elif emoji.emoji_count(option[:3]):
                emojis.append(option[:3])
            # Use letter if it wasn't found
            else:
                option = emojiDict.LETTERS[i] + " " + option
                emojis.append(emojiDict.LETTERS[i])
     
            embed.add_field(name=option, value=progress_bar(), inline=False)
            i += 1

        # Send message and save it
        response: PartialInteractionMessage = await interaction.response.send_message(embed=embed)
        message: Message = await response.fetch()
        self.polls[message.id] = emojis
        self.poll_ids[poll_id] = message.id

        # Add reactions
        for e in emojis:
            await message.add_reaction(e)
        
        # Save polls to file
        dataManager.save_polls(self.polls, self.poll_ids)
    

    @slash_command(guild_ids=TEST_GUILDS, description="Locks a poll so users won't be able to vote anymore.", force_global=PRODUCTION)
    async def lock_poll(self, interaction: Interaction, poll_id: str):
        # Log
        self.logger.log_info(interaction.user.name + "#" + str(interaction.user.discriminator) + " has called command: lock_poll " + poll_id + ".")

        # Return if user doesn't have permission to run command
        if not access.has_access(interaction.user, interaction.guild, "Manage Polls"):
            await interaction.response.send_message("🚫 FAILED. You don't have permission to lock polls.", ephemeral=True)
            return
            
        # Return if poll doesn't exist
        if not poll_id in self.poll_ids.keys():
            await interaction.response.send_message("🚫 FAILED. Poll with ID " + poll_id +" wasn't found.", ephemeral=True)
            return
            
        # Lock it
        poll = self.poll_ids.pop(poll_id)
        self.polls.pop(poll)

        dataManager.save_polls(self.polls, self.poll_ids)
        await interaction.response.send_message("✅ Successfully locked poll.", ephemeral=True)
    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event: nextcord.RawReactionActionEvent):
        # Cancel if there are no polls
        if len(self.polls) == 0:
            return
            
        # Cancel if message isn't a poll
        if not event.message_id in self.polls.keys():
            return
        
        # Cancel if reaction author is bot
        if event.user_id == self.client.user.id:
            return

        # Remove reaction if it isn't valid
        message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)

        if event.user_id != self.client.user.id and not event.emoji.name in self.polls[event.message_id]:
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
        await self.update_poll(message)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, event: nextcord.RawReactionActionEvent):
        # Cancel if there are no polls
        if len(self.polls) == 0:
            return
        
        # Cancel if message isn't a poll
        if not event.message_id in self.polls.keys():
            return
        
        # Cancel if reaction is removed by bot
        if event.user_id == self.client.user.id:
            return
        
        # Update poll
        message: Message = await self.client.get_channel(event.channel_id).fetch_message(event.message_id)
        await self.update_poll(message)


    @commands.Cog.listener()
    async def on_raw_message_delete(self, event: RawMessageDeleteEvent):
        if event.message_id in list(self.polls.keys()):
            # Log
            self.logger.log_info("Poll " + str(event.message_id) + " message was deleted. Removing poll object.")

            # Remove from lists
            self.polls.pop(event.message_id)
            values = list(self.poll_ids.values())
            for i in range(len(values)):
                if values[i] == event.message_id:
                    self.poll_ids.pop(list(self.poll_ids.keys())[i])
                    break

            # Save them
            dataManager.save_polls(self.polls, self.poll_ids)

    
    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, event: nextcord.RawBulkMessageDeleteEvent):
        for id in event.message_ids:
            if id in list(self.polls.keys()):
                # Log
                self.logger.log_info("Poll " + str(id) + " message was deleted. Removing poll object.")
                
                # Remove from lists
                self.polls.pop(id)
                values = list(self.poll_ids.values())
                for i in range(len(values)):
                    if values[i] == id:
                        self.poll_ids.pop(list(self.poll_ids.keys())[i])
                        break
                
                # Save them
                dataManager.save_polls(self.polls, self.poll_ids)


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

    bar = "`"
    for i in range(percentage):
        bar += "█"
        
    for i in range(30 - percentage):
        bar += " "

    bar += "` | " + str(round((value / max) * 1000) / 10) + "% (" + str(value) + ")"

    return bar


def generate_id() -> str:
    characters = "0123456789abcdefghijklmnopqrstuvwxyz"
    id = ""
    for i in range(10):
        id += characters[randint(0, len(characters)-1)]
    return id


def load(client: commands.Bot):
    client.add_cog(Polls(client))