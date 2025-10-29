import discord
from discord.ext import commands
import os # Import the os module to access environment variables

# 1. Define Intents
# You need 'message_content' intent if the bot reads message content (like 'ping').
# This must also be enabled in the Discord Developer Portal.
intents = discord.Intents.default()
intents.message_content = True

# 2. Create the Bot object
# Set the command prefix to '!'
bot = commands.Bot(command_prefix='!', intents=intents)

# 3. Event: Bot is ready
@bot.event
async def on_ready():
    print(f'🚀 Bot logged in as {bot.user} (ID: {bot.user.id})')
    print('----------------------------------------------------')

# 4. Text command (e.g., typing !ping)
@bot.command()
async def ping(ctx):
    # ctx is the "context" of the command invocation
    await ctx.send('Pong!')

# 5. Run the Bot
# ALWAYS load the token from an environment variable for security
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") 
if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("ERROR: DISCORD_BOT_TOKEN environment variable not found.")