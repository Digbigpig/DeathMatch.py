import discord
import logging
import asyncio
from discord.ext import commands

description = '''Runescape based fighting game for Discord'''
logging.basicConfig(level=logging.INFO)
startup_extensions = ['members', 'rng', 'ping', 'DMMain']

bot = commands.Bot(command_prefix='.', description=description)
client = discord.Client()





@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('Connected to ' + str(len(client.servers)) + ' servers | Connected to ' + str(
        len(set(client.get_all_members()))) + ' users ')
    print('------')
    # await bot.edit_profile(username="Death Match")             # EDIT BOTS USERNAME ( COMMENT OUT AFTER RUN )

@bot.command()
async def load(extension_name: str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command()
async def unload(extension_name : str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))

@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)

@bot.command()
async def repeat(times : int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content)

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))


    bot.run('TOKEN')
