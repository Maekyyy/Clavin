import discord
from discord.ext import commands
import os
import threading # Required to run the Flask web server in the background
from flask import Flask # Import Flask

# --- FLASK FUNCTION FOR CLOUD RUN HEALTH CHECK ---
def run_flask_app():
    # Cloud Run requires listening on port 8080 (or the one provided by the environment variable)
    app = Flask(__name__)
    
    # Simple health check path that returns status 200
    @app.route('/')
    def home():
        return "Discord bot is alive!", 200

    # Run the Flask server. It must bind to 0.0.0.0 and use the PORT environment variable.
    # Cloud Run will use this to confirm the container started successfully.
    # We use 'waitress' or a similar WSGI server in production, but Flask's built-in server is enough for a simple health check.
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
# -----------------------------------------------

# 1. Define Intents (as before)
intents = discord.Intents.default()
intents.message_content = True 

# 2. Create the Bot object
bot = commands.Bot(command_prefix='!', intents=intents)

# 3. Event: Bot is ready
@bot.event
async def on_ready():
    print(f'🚀 Bot logged in as {bot.user} (ID: {bot.user.id})')
    print('----------------------------------------------------')

# 4. Text command (example)
@bot.command()
async def ping(ctx):
    await ctx.send('Pong! I am running on Google Cloud Run.')

# 5. Run the Bot
if __name__ == '__main__':
    # 1. Start the Flask web server in a separate thread
    # This prevents Flask from blocking the main Discord bot loop (asyncio)
    threading.Thread(target=run_flask_app).start()
    
    # 2. Run the Discord bot
    BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") 
    if BOT_TOKEN:
        print("Starting Discord bot client...")
        # Note: discord.py is inherently async, but bot.run is synchronous here.
        bot.run(BOT_TOKEN)
    else:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not found.")