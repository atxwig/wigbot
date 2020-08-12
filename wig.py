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

from commands.roles.roles import Roles

# globals
guild_id = 670469511572488223  # TODO: find a way to not hardcode
cached_invite_list = {}
token = 0


DATABASE_URL = os.environ['DATABASE_URL'] # connect to postgres if online
connection = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = connection.cursor()


# bot description
command_prefix = '-'
description = "wigwigwig"
bot = commands.Bot(command_prefix=command_prefix, description=description,
                   case_insensitive=True)


bot.add_cog(Roles(bot))


# start up
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    print("caching invites . . .")
    cursor.execute(''' SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'invites' ''')
    if cursor.fetchone()[0] == 0:
        # init database
        cursor.execute(''' CREATE TABLE invites (
            id       text,
            location text
        )''')
        connection.commit()

        invite_list = await bot.get_guild(guild_id).invites()
        for invite in invite_list:
            data_string = str((invite.id,0))
            print(data_string)
            entry_string = f"INSERT INTO invites VALUES {data_string}"
            cursor.execute(entry_string)
        connection.commit()

    cursor.execute(''' SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'defaults' ''')
    if cursor.fetchone()[0] == 0:
        # init database
        cursor.execute(''' CREATE TABLE defaults (
            name  text,
            value text
        )''')
        data_string = str(("invite", 0))
        entry_string = f"INSERT INTO defaults VALUES {data_string}"
        cursor.execute(entry_string)
        connection.commit()

    await cache_invites()
    print("done")

    game = discord.Game("wigwigwig")
    await bot.change_presence(activity = game)


# set channel command
@bot.command()
async def setchannel(ctx):
    query = ''' UPDATE defaults SET value=%s WHERE name=%s '''
    params = (ctx.message.channel.id, "invite")
    cursor.execute(query, params)
    connection.commit()
    await ctx.send(f"{ctx.message.channel.mention} has been set as the default channel for invites!")


# get invite channel
@bot.command()
async def getinvitechannel(ctx):
    query = ''' SELECT value FROM defaults WHERE name=%s '''
    params = ("invite",)
    cursor.execute(query, params)
    value = cursor.fetchone()
    channel_id = int(value[0])
    if channel_id:
        await ctx.send(f"The default channel is {bot.get_channel(channel_id).mention}.")
    else:
        await ctx.send(f"The default channel for invites hasn't been set yet :c")


# member join
@bot.event
async def on_member_join(member):
    invite_id_list = await member.guild.invites()  # fetch current invite uses

    curr_invite_list = {}
    for invite in invite_id_list:
        curr_invite_list[invite.id] = invite.uses
    message = f"**{member.name}** has joined!"

    for invite in invite_id_list:
        if curr_invite_list[invite.id] != cached_invite_list[invite.id]:
            message += f" Invited by **{invite.inviter.display_name}** from **{invite.code}**"
            query = ''' SELECT location FROM invites WHERE id=%s '''
            params = (str(invite.id),)
            cursor.execute(query, params)
            loc = cursor.fetchone()
            if loc[0] is not "0":
                message += f", located at **{str(loc[0])}**"
            break
    
    await cache_invites()
    cursor.execute(''' SELECT value FROM defaults WHERE name=%s ''', ("invite",))
    value = cursor.fetchone()
    channel_id = int(value[0])
    if channel_id:
        await bot.get_channel(channel_id).send(message)
    # else:
        # TODO: make bot dm me if this messes up


# invite creation
@bot.event
async def on_invite_create(invite):
    cached_invite_list[invite.id] = 0
    data_string = str((invite.id,0))
    entry_string = f"INSERT INTO invites VALUES {data_string}"
    cursor.execute(entry_string)
    connection.commit()
    
    cursor.execute(''' SELECT value FROM defaults WHERE name=%s ''', ("invite",))
    value = cursor.fetchone()
    channel_id = int(value[0])
    if channel_id:
        await bot.get_channel(channel_id).send(
            f"Invite **{invite.id}** has been created by **{invite.inviter}**")
    # else:
        # TODO: make bot dm me if this messes up


# gets current invites
async def cache_invites():
    invite_id_list = await bot.get_guild(guild_id).invites()

    for invite in invite_id_list:
        cached_invite_list[invite.id] = invite.uses
        print(f"added invite {invite.id}")


# test command
@bot.command()
async def test(ctx):
    await ctx.send("wigwigwig")


# help command
@bot.command()
async def helpme(ctx):
    embed = discord.Embed(title="TWIGGY COMMANDS",
                          description=f"Command prefix = {command_prefix}")
    embed.add_field(
        name=f"{command_prefix}test", value="Sends wigwigwig", inline=False)

    embed.add_field(name=f"{command_prefix}setchannel",
                    value="Sets current channel to default channel. (Right now just picks what channel to send the invite messages to.", inline=False)

    embed.add_field(name=f"{command_prefix}hug [@user]",
                    value="Sends a cute hug to whoever you at uwu", inline=False)

    await ctx.send(embed=embed)

    
# hug command
@bot.command()
async def hug(ctx, member_id):
    member_id = member_id[3:-1]
    member = ctx.message.guild.get_member(int(member_id))
    if member:
        await ctx.send(f"{ctx.message.author.mention} is omega cute and hugged {member.mention}!")
    else:
        await ctx.send("I couldn't find that user D:")


# update invite command
@bot.command()
async def update(ctx, invite_id, *, location):
    params = (str(location), str(invite_id))
    query = ''' UPDATE invites SET location=%s WHERE id=%s '''
    cursor.execute(query, params)
    if cursor.rowcount < 1:
        await ctx.send(f"I couldn't find **{invite_id}** in my invites database :c")
    else:
        await ctx.send(f"The new location of **{invite_id}** is now **{location}**")
    connection.commit()


# fetch invite info
@bot.command()
async def getinfo(ctx, invite_id):
    query = ''' SELECT location FROM invites WHERE id=%s '''
    params = (str(invite_id),)
    cursor.execute(query, params)
    message = f"I couldn't find **{invite_id}** in my invites database :c"
    loc = cursor.fetchone()
    if loc[0] is not "0":
        message = f"The location of **{invite_id}** is **{loc[0]}**"
    await ctx.send(message)


# mc whitelist command
@bot.command()
async def whitelist(ctx, username):
    await bot.get_channel(737927157942190140).send(f"whitelist add {username}")
    def check(m):
        return "Added" in m.content \
            and m.channel.id == 737927157942190140

    try:
        msg = await bot.wait_for('message', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"Something went wrong :c")
    else:
        await ctx.send(f"Added {username} to the whitelist <3")


bot.run(os.environ.get('BOT_TOKEN'))
