from discord.ext import commands

import discord
import os

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = "&"

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix=PREFIX,
    description="The awesome McGyver TCA bot",
    guild_subscriptions=True,
    intents=intents
)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Help"))

    print(f"{bot.user} has connected to Discord!")


@bot.event
async def on_message(message):
    """
    Function executed on each message received
    """
    if not message.author.bot:
        if message.content.lower() == "ping":
            await message.channel.send("pong")
            await bot.change_presence(activity=discord.Game(name="Ping-Ponging"))

        if message.content.lower().replace(" ", "") in ["tccalendarbot"] or bot.user in message.mentions:
            await message.channel.send("Hello, I am a calendar! :eyes: <:dobby:823315794472730655>\n")

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    """
    Function executed on each command error made
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("I believe you totally failed your command")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("I believe you forgot something important in your command :thinking:")
    if isinstance(error, (commands.CheckFailure, commands.MissingPermissions)):
        await ctx.send("I believe you cannot use that")
    if isinstance(error, discord.Forbidden):
        await ctx.send("Stop asking me to do something I cannot")


if __name__ == "__main__":
    bot.load_extension("cogs.calendar.cog")
    bot.run(TOKEN)
