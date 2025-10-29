import discord
from discord.ext import commands
import os
import threading
from flask import Flask
import asyncio

# --- FLASK FUNCTION FOR CLOUD RUN HEALTH CHECK ---
def run_flask_app():
    # Cloud Run requires listening on port 8080 (or the one provided by the environment variable)
    app = Flask(__name__)
    
    # Simple health check path that returns status 200
    @app.route('/')
    def home():
        return "Discord bot is alive!", 200

    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
# -----------------------------------------------

# 1. Define Intents (we keep them)
# We need 'message_content' for regular message handling, but less critical for slash commands.
intents = discord.Intents.default()
intents.message_content = True 

# 2. Create the Bot object
# No command_prefix needed for slash commands, but we keep it just in case
bot = commands.Bot(command_prefix='!', intents=intents)

# 3. Cog Loading Function (New)
async def load_cogs():
    # Load the new slash command module 'basic.py' from the 'cogs' folder
    try:
        await bot.load_extension('cogs.basic')
        print("✅ Successfully loaded cogs.")
    except Exception as e:
        print(f"❌ Failed to load cogs: {e}")

# 4. Event: Bot is ready
@bot.event
async def on_ready():
    print(f'🚀 Bot logged in as {bot.user} (ID: {bot.user.id})')
    # Load cogs only when bot is ready
    await load_cogs()
    # Syncing global slash commands with Discord API
    synced = await bot.tree.sync()
    print(f"🔄 Synced {len(synced)} slash commands globally.")
    print('----------------------------------------------------')

# 5. Run the Bot
if __name__ == '__main__':
    # 1. Start the Flask web server in a separate thread
    threading.Thread(target=run_flask_app).start()
    
    # 2. Run the Discord bot
    BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") 
    if BOT_TOKEN:
        print("Starting Discord bot client...")
        bot.run(BOT_TOKEN)
    else:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not found.")