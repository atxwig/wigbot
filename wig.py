import discord
from discord.ext import commands
import os
import random
import pathlib
import sys
import io
import traceback


# bot description
command_prefix = '-'
description = "wigwigwig"
bot = commands.Bot(command_prefix=command_prefix, description=description,
                   case_insensitive=True)


# globals
guild_id = 550143114417930250  # TODO: find a way to not hardcode
cached_invite_list = {}
default_channel_id = None

# token = 0
# f = open("secrets.txt", "r") # fetch token from secrets file
# lines = f.readlines()
# for line in lines:
#     if "TOKEN" in line:
#         line_list = line.split("=")
#         token = line_list[1]

# start up
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    print("caching invites . . .")
    await cache_invites()
    print("done")


# set channel command
@bot.command()
async def setchannel(ctx):
    global default_channel_id
    default_channel_id = ctx.message.channel.id
    await ctx.send(f"{bot.get_channel(default_channel_id).mention} has been set as the default channel!")

# get channel command
@bot.command()
async def getchannel(ctx):
    global default_channel_id
    await ctx.send(f"The default channel is {bot.get_channel(default_channel_id).mention}.")

# member join
@bot.event
async def on_member_join(member):
    global default_channel_id
    invite_id_list = await member.guild.invites()  # fetch current invite uses

    curr_invite_list = {}
    for invite in invite_id_list:
        curr_invite_list[invite.id] = invite.uses
    message = f"**{member.name}** has joined!"

    for invite in invite_id_list:
        if curr_invite_list[invite.id] != cached_invite_list[invite.id]:
            message += f" Invited from **{invite.code}** by **{invite.inviter.display_name}**"
            break

    await cache_invites()
    await bot.get_channel(default_channel_id).send(message)


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


bot.run(os.environ.get('BOT_TOKEN'))
# bot.run(token)
