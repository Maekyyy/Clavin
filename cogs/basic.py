import discord
from discord.ext import commands

# Cogs are classes that inherit from commands.Cog
class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # You can add setup logic here if needed

    # --- SLASH COMMAND EXAMPLE ---
    # The commands.slash_command() decorator registers the command as a slash command
    @commands.slash_command(
        name="synctest", 
        description="Tests if the bot is alive and slash commands are working."
    )
    async def slash_test(self, ctx):
        # ctx here is ApplicationContext, specific to slash commands
        
        # We use ctx.respond for slash command responses
        await ctx.respond("✅ **Pong!** Slash command successful. Bot is running on Google Cloud Run.")

    # --- SLASH COMMAND WITH ARGUMENTS EXAMPLE ---
    @commands.slash_command(name="hello", description="Says hello to the user.")
    @discord.option(
        name="name",
        description="The name of the person to greet.",
        required=True
    )
    async def greet(self, ctx: discord.ApplicationContext, name: str):
        await ctx.respond(f"👋 Hello, {name}! Nice to meet you.")


# --- COG SETUP FUNCTION ---
# This function is REQUIRED by py-cord to load the cog
def setup(bot):
    bot.add_cog(Basic(bot))