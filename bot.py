import os
from twitchio.ext import commands
from sheets import Sheets
import datetime

TOKEN    = 'p7ckk9y6xzepawmazrtb8cg7qtx0di' # API Token
PREFIX   = '!'    # Command syntax
LIST     = 'https://docs.google.com/spreadsheets/d/1mz-b8zojmVwpVQ8qdL9Y-5YCB1Jly62Jn60f7gS-HDc'   # Link to sheets
CHANNELS = ['Mendo']


_Sheets = Sheets()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix=PREFIX, initial_channels=CHANNELS)

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        await self.join_channels(CHANNELS)

    # Listen for messages from viewers.
    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot, ignoring self messages.
        if message.echo:
            print(f'Bot: {message.content}')
            return

        # Print the contents of our message to console...
        print(f'Message received by: {message.author.name}')

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        # SENDS MESSAGE TO COMMANDS TO SEE IF MATCHING COMMAND
        await self.handle_commands(message)

    def is_mod(self, ctx: commands.Context):
        return ctx.author.is_mod or ctx.author.name == "zryu"

    @commands.command(name='ping')
    async def ping(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'pong {ctx.author.name}!')

    # Link list. (No need to link spreadsheet)
    @commands.command(name='list', aliases=['sheets', 'sheet', 'link'])
    async def list(self, ctx: commands.Context):
        # await ctx.send(f'Heres the link: {LIST}')
        return


    # Add players to list.
    @commands.command(name='add')
    async def add(self, ctx: commands.Context):
        # check if mod or I
        if not self.is_mod(ctx):
            await ctx.send("Only mods can use this command.")
            return

        # removes command from message
        message = ctx.message.content.replace(f'{PREFIX}add', '')

        # Splits message into Name and Character/MatchID
        parts = message.split(' ')

        # Removes empty indexs (this can be refactored)
        for part in parts:
            if part == '':
                parts.remove('')
            if part == '\U000e0000':
                parts.remove('\U000e0000')

        # Check if valid message format (can be refactored better)
        if len(parts) != 2:
            await ctx.send(f'Invalid format. Format should be:{PREFIX}add [Name] [Character/MatchID].')

        matchID = ""
        if parts[1].isnumeric():
            matchID = parts[1]
        date = datetime.datetime.now().date().strftime('%m/%d')


        # Add character to sheet.
        added = _Sheets.AddInfo(parts[0], parts[1], date)

        # send return message
        if not added[0]:
            await ctx.send(f'{added[1]}')
            return

        await ctx.send(f'{added[1]}')

    @commands.command(name='characters', aliases=["chars", "char"])
    async def characters(self, ctx: commands):
        # checks how the user called the command and sanitizes string.
        if ctx.message.content.startswith(f'{PREFIX}chars '):
            name = ctx.message.content.replace(f'{PREFIX}chars ', "")
        else:
            name = ctx.message.content.replace(f'{PREFIX}characters ', "")

        # Returns info
        await ctx.send(f'{_Sheets.GetPlayerCharacters(name)}')

    @commands.command(name='avoids')
    async def get_avoids(self, ctx: commands):
        avoids = _Sheets.GetAvoids()
        message = "Current avoids are: "

        if avoids == None:
            await ctx.send(f'Currently there are no avoids.')
            return

        for i, avoid in enumerate(avoids):
            if avoid is not None:  # Check if avoid is not None before concatenating
                if i == len(avoids):
                    message += avoid
                    break

                message += avoid + ", "

        await ctx.send(f'{message}')

    @commands.command(name="addavoid")
    async def add_avoid(self, ctx: commands):

        if not self.is_mod(ctx):
            await ctx.send("Only mods can use this command.")
            return

        name = ctx.message.content.replace(f'{PREFIX}addavoid ', "")
        name = name.strip()

        _Sheets.AddAvoid(name)

        await ctx.send(f'Avoids have been updated.')


bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.






