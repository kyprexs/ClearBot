import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
import logging

# Initialize colorama
init(autoreset=True)

# Emoji and color helpers
INFO = f"{Fore.GREEN}[🟢 INFO]{Style.RESET_ALL}"
SUCCESS = f"{Fore.LIGHTGREEN_EX}[✅ SUCCESS]{Style.RESET_ALL}"
WARNING = f"{Fore.YELLOW}[⚠️ WARNING]{Style.RESET_ALL}"
ERROR = f"{Fore.RED}[❌ ERROR]{Style.RESET_ALL}"

# Load environment variables
load_dotenv()

# Debug flag (set DEBUG=1 in .env or environment to enable verbose logs)
DEBUG = os.getenv('DEBUG', '0') == '1'

# Suppress discord.py logs unless debugging
if not DEBUG:
    logging.getLogger('discord').setLevel(logging.CRITICAL)
    logging.getLogger('discord.http').setLevel(logging.CRITICAL)
    logging.getLogger('discord.gateway').setLevel(logging.CRITICAL)
    logging.getLogger('discord.client').setLevel(logging.CRITICAL)
    logging.getLogger('discord.state').setLevel(logging.CRITICAL)
    logging.getLogger('discord.voice_client').setLevel(logging.CRITICAL)
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)
else:
    print(f"{WARNING} Debug mode enabled. Discord library logs will be shown.")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"{SUCCESS} {bot.user} has connected to Discord!")
    try:
        synced = await bot.tree.sync()
        print(f"{SUCCESS} Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"{ERROR} Failed to sync commands: {e}")

@bot.tree.command(name="clear", description="Clear all messages in the current channel")
@app_commands.describe(
    amount="Number of messages to delete (default: all messages)"
)
async def clear(interaction: discord.Interaction, amount: int = None):
    # Check if user has manage messages permission
    if not interaction.channel.permissions_for(interaction.user).manage_messages:
        await interaction.response.send_message("❌ You don't have permission to delete messages!", ephemeral=True)
        return
    
    # Check if bot has manage messages permission
    if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
        await interaction.response.send_message("❌ I don't have permission to delete messages!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        deleted_count = 0
        
        if amount is None:
            # Delete all messages in the channel
            async for message in interaction.channel.history(limit=None):
                try:
                    await message.delete()
                    deleted_count += 1
                except discord.Forbidden:
                    # Skip messages we can't delete (e.g., older than 14 days)
                    continue
                except discord.HTTPException:
                    # Skip messages that can't be deleted for other reasons
                    continue
        else:
            # Delete specified number of messages
            async for message in interaction.channel.history(limit=amount):
                try:
                    await message.delete()
                    deleted_count += 1
                except discord.Forbidden:
                    # Skip messages we can't delete
                    continue
                except discord.HTTPException:
                    # Skip messages that can't be deleted for other reasons
                    continue
        
        if deleted_count > 0:
            print(f"{SUCCESS} Deleted {deleted_count} message(s) in #{interaction.channel.name}")
            await interaction.followup.send(f"✅ Successfully deleted {deleted_count} message(s)!", ephemeral=True)
        else:
            print(f"{WARNING} No messages were deleted in #{interaction.channel.name}")
            await interaction.followup.send("ℹ️ No messages were deleted. This might be due to message age limits or permissions.", ephemeral=True)
            
    except Exception as e:
        print(f"{ERROR} An error occurred while clearing messages: {str(e)}")
        await interaction.followup.send(f"❌ An error occurred while clearing messages: {str(e)}", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print(f"{ERROR} No Discord token found! Please set DISCORD_TOKEN in your .env file.")
        exit(1)
    print(f"{INFO} Starting Discord bot...")
    print(f"{INFO} Make sure to invite the bot to your server with the required permissions!")
    bot.run(token) 