import discord
from discord.ext import commands
import os
import threading
from flask import Flask
import asyncio

# --- FLASK FUNCTION FOR CLOUD RUN HEALTH CHECK ---
# Must run in a separate thread to keep the container alive.
def run_flask_app():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Discord bot is alive!", 200

    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
# -----------------------------------------------

# 1. Define Intents 
intents = discord.Intents.default()
intents.message_content = True 

# 2. Create the Bot object
bot = commands.Bot(command_prefix='!', intents=intents)

# 3. Cog Loading Function (Corrected to be asynchronous)
async def load_cogs():
    try:
        await bot.load_extension('cogs.basic') 
        print("✅ Successfully loaded cogs.")
    except Exception as e:
        print(f"❌ Failed to load cogs: {e}")

# 4. Event: Bot is ready (Final corrected sync method)
@bot.event
async def on_ready():
    print(f'🚀 Bot logged in as {bot.user} (ID: {bot.user.id})')
    
    await load_cogs() 
    
    # Use bot.tree.sync() for slash commands
    synced = await bot.tree.sync() 
    
    # Safely check length
    if synced is not None:
        print(f"🔄 Synced {len(synced)} slash commands globally.")
    else:
        print("❌ WARNING: Slash command sync returned None.")
        
    print('----------------------------------------------------')

# 5. Run the Bot
if __name__ == '__main__':
    # 1. Start the Flask web server in a separate daemon thread
    threading.Thread(target=run_flask_app, daemon=True).start()
    
    # 2. Run the Discord bot
    BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") 
    if BOT_TOKEN:
        print("Starting Discord bot client...")
        bot.run(BOT_TOKEN)
    else:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not found.")