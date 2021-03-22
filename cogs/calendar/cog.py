from datetime import datetime, timedelta
from discord.ext import commands, tasks
from .utils import format_response, get_course_by_date, download_calendar, get_week_calendar, get_offset

import discord
import os
import re

ROOT_CALENDAR = "cogs/calendar/Assets"


def setup(bot):
    """
    Function to setup the bot by enabling CogCalendar
    """
    print("Help command load")
    bot.add_cog(CogCalendar(bot))


class CogCalendar(commands.Cog):
    """
    Class CogCalendar having all the commands to get the calendar
    """

    def __init__(self, bot):
        """
        Init the CogCalendar
        """
        self.bot = bot
        self.update_calendars.start()
        self.dobby = None

    def cog_unload(self):
        """
        Cancel calendar updates on cog unload
        """
        self.update_calendars.cancel()

    @commands.command(aliases=["Calendar", "cal", "week"])
    async def calendar(self, ctx, arg="3TCA", offset="+0"):
        """
        Get the calendar of a week
        """
        # Get the dobby emoji from the server
        self.dobby = self.bot.get_emoji(823315794472730655)

        if re.match(r"(([34])(TC|tc|Tc|tC)([123Aa])|([5])(TC|tc|Tc|tC)([123]))", arg):
            await self.bot.change_presence(
                activity=discord.Activity(name=f"Calendrier des {arg}", type=discord.ActivityType.watching)
            )
            year = arg[0]
            if arg[-1].isnumeric():
                group = arg[-1]
            else:
                group = "A"
            calendar_path = ROOT_CALENDAR + f"/{year}TC{group}.ical"
            offset = get_offset(offset)
            calendar = get_week_calendar(calendar_path=calendar_path, offset=offset, dobby=self.dobby)
            await ctx.send(
                content="@Reynald Lambolez#1305 pour que tu ne sois pas en retard...",
                embed=calendar
            )
        else:
            await ctx.send("please enter a valid input <year>TC<group>")

    @commands.command(aliases=["Today", "aujourd'hui", "auj", "tod"])
    async def today(self, ctx, arg="3TCA"):
        """
        Get the agenda of the current day
        """
        if re.match(r"(([34])(TC|tc|Tc|tC)([123Aa])|([5])(TC|tc|Tc|tC)([123]))", arg):
            await self.bot.change_presence(
                activity=discord.Activity(name=f"Calendrier des {arg}", type=discord.ActivityType.watching)
            )

            year = arg[0]
            if arg[-1].isnumeric():
                group = arg[-1]
            else:
                group = "A"

            response = "@Reynald Lambolez#1305 pour que tu ne sois pas en retard...\n"
            courses = get_course_by_date(
                prompt_date=datetime.now().date(),
                calendar_path=ROOT_CALENDAR + f"/{year}TC{group}.ical"
            )
            if not courses:
                await ctx.send("It's <:dobby:823315794472730655> time")
            else:
                for course in courses:
                    response += format_response(course) + "\n"
                await ctx.send(response)
        else:
            await ctx.send("please enter a valid prompt <year>TC<group>")

    @commands.command(aliases=["Tomorow", "demain", "tom"])
    async def tomorrow(self, ctx, arg="3TCA"):
        """
        Get the agenda of the next day
        """
        if re.match(r"(([34])(TC|tc|Tc|tC)([123Aa])|([5])(TC|tc|Tc|tC)([123]))", arg):
            await self.bot.change_presence(
                activity=discord.Activity(name=f"Calendrier des {arg}", type=discord.ActivityType.watching)
            )
            year = arg[0]
            if arg[-1].isnumeric():
                group = arg[-1]
            else:
                group = "A"
            response = "@Reynald Lambolez#1305 pour que tu ne sois pas en retard...\n"
            tomorrow = datetime.now() + timedelta(days=1)
            courses = get_course_by_date(
                prompt_date=tomorrow.date(),
                calendar_path=ROOT_CALENDAR + f"/{year}TC{group}.ical"
            )
            if not courses:
                await ctx.send("It's <:dobby:823315794472730655> time")
            else:
                for course in courses:
                    response += format_response(course) + "\n"
                await ctx.send(response)
        else:
            await ctx.send("please enter a valid input <year>TC<group>")

    @tasks.loop(hours=24)
    async def update_calendars(self):
        """
        Update the calendars on init and each 24 hours
        """
        print("Deleting calendar assets")
        assets_dir = "cogs/calendar/Assets"
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
        for file in os.listdir(assets_dir):
            os.remove(os.path.join(assets_dir, file))

        download_calendar()
