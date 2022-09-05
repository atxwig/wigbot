import discord
from discord.ext import commands
import os
import random
import pathlib
import sys
import io
import traceback
import sqlite3 # connect, commit
import asyncio
import psycopg2

# from commands.roles.roles import Roles
from commands.invites.invites import Invites

# globals
GUILD_ID = 550143114417930250
DEV_ID   = [146450066943639552, 412826486446227457]
TOKEN = 0


DATABASE_URL = os.environ['DATABASE_URL'] # connect to postgres if online
CONNECTION = psycopg2.connect(DATABASE_URL, sslmode='require')
CURSOR = CONNECTION.cursor()

# # ----- SQLLITE ----- #
# CONNECTION = sqlite3.connect("twiggy.db")
# CURSOR     = CONNECTION.cursor()


# bot description
COMMAND_PREFIX = '-'
DESCRIPTION = "wigwigwig"
INTENTS = discord.Intents.all()
BOT = commands.Bot(command_prefix=COMMAND_PREFIX, description=DESCRIPTION,
                   case_insensitive=True, intents=INTENTS)


# start up
@BOT.event
async def on_ready():
    print(f"Logged in as {BOT.user.name}")

    await BOT.add_cog(Invites(BOT))

    cog = BOT.get_cog('Invites')
    commands = cog.get_commands()
    print([c.name for c in commands])

    CURSOR.execute(''' SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'invites' ''') # postgres
    # CURSOR.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='invites' ''')
    if CURSOR.fetchone()[0] == 0:
        # init database
        CURSOR.execute(''' CREATE TABLE invites (
            id       text,
            location text
        )''')
        CONNECTION.commit()

        for invite in await BOT.get_guild(GUILD_ID).invites():
            data_string = str((invite.id,0))
            print(data_string)
            entry_string = f"INSERT INTO invites VALUES {data_string}"
            CURSOR.execute(entry_string)
        CONNECTION.commit()

    CURSOR.execute(''' SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'defaults' ''') # postgres
    # CURSOR.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='defaults' ''')
    if CURSOR.fetchone()[0] == 0:
        # init database
        CURSOR.execute(''' CREATE TABLE defaults (
            name  text,
            value text
        )''')
        data_string = str(("invite", 0))
        entry_string = f"INSERT INTO defaults VALUES {data_string}"
        CURSOR.execute(entry_string)
        CONNECTION.commit()

    await Invites.cache_invites(await BOT.get_guild(GUILD_ID).invites())
    print("done")

    game = discord.Game("wigwigwig")
    await BOT.change_presence(activity = game)


# test command
@BOT.command()
async def test(ctx):
    await ctx.send("wigwigwig")


# help command
@BOT.command()
async def helpme(ctx):
    embed = discord.Embed(title="TWIGGY COMMANDS",
                          description=f"Command prefix = {COMMAND_PREFIX}")
    embed.add_field(
        name=f"{COMMAND_PREFIX}test", value="Sends wigwigwig", inline=False)

    embed.add_field(name=f"{COMMAND_PREFIX}setchannel",
                    value="Sets current channel to default channel. (Right now just picks what channel to send the invite messages to.", inline=False)

    embed.add_field(name=f"{COMMAND_PREFIX}hug [@user]",
                    value="Sends a cute hug to whoever you at uwu", inline=False)

    await ctx.send(embed=embed)

    
# hug command
@BOT.command()
async def hug(ctx, member_id):
    member_id = member_id[3:-1]
    member = ctx.message.guild.get_member(int(member_id))
    if member:
        await ctx.send(f"{ctx.message.author.mention} is omega cute and hugged {member.mention}!")
    else:
        await ctx.send("I couldn't find that user D:")


# mc whitelist command
@BOT.command()
async def whitelist(ctx, username):
    await BOT.get_channel(737927157942190140).send(f"whitelist add {username}")
    def check(m):
        return "Added" in m.content \
            and m.channel.id == 737927157942190140

    try:
        msg = await BOT.wait_for('message', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        msg = f"Something went wrong :c "
        for id in DEV_ID:    
            msg += f'{BOT.get_guild(GUILD_ID).get_member(id).mention} '
        await ctx.send(msg)
    else:
        await ctx.send(f"Added {username} to the whitelist <3")


BOT.run(os.environ.get('BOT_TOKEN'))