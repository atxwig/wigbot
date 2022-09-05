import os
import random
import pathlib
import sys
import io
import traceback
import sqlite3 # connect, commit
import asyncio
import psycopg2

import discord
from discord.ext import commands
import sqlite3

DATABASE_URL = os.environ['DATABASE_URL'] # connect to postgres if online
CONNECTION = psycopg2.connect(DATABASE_URL, sslmode='require')
CURSOR = CONNECTION.cursor()

# # ----- SQLLITE ----- #
# CONNECTION = sqlite3.connect("twiggy.db")
# CURSOR     = CONNECTION.cursor()

GUILD_ID = 550143114417930250
CACHED_INVITE_LIST = {}


class Invites(commands.Cog):
    
    def __init__(self, bot):
        self.BOT = bot
        print("invites initilized !!!")

    # gets current invites
    async def cache_invites(invite_id_list):
        for invite in invite_id_list:
            CACHED_INVITE_LIST[invite.id] = invite.uses
            print(f"added invite {invite.id}")


    # set channel command
    @commands.command()
    async def setchannel(self, ctx):
        query = ''' UPDATE defaults SET value=%s WHERE name=%s '''
        # query = ''' UPDATE defaults SET value=? WHERE name=? '''
        params = (ctx.message.channel.id, "invite")
        CURSOR.execute(query, params)
        CONNECTION.commit()
        await ctx.send(f"{ctx.message.channel.mention} has been set as the default channel for invites!")


    # get invite channel
    @commands.command()
    async def getinvitechannel(self, ctx):
        query = ''' SELECT value FROM defaults WHERE name=%s '''
        # query = ''' SELECT value FROM defaults WHERE name=? '''
        params = ("invite",)
        CURSOR.execute(query, params)
        value = CURSOR.fetchone()
        channel_id = int(value[0])
        if channel_id:
            await ctx.send(f"The default channel is {self.BOT.get_channel(channel_id).mention}.")
        else:
            await ctx.send(f"The default channel for invites hasn't been set yet :c")


    # member join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        invite_id_list = await member.guild.invites()  # fetch current invite uses

        curr_invite_list = {}
        for invite in invite_id_list:
            curr_invite_list[invite.id] = invite.uses
        message = f"**{member.name}** has joined!"

        for invite in invite_id_list:
            if curr_invite_list[invite.id] != CACHED_INVITE_LIST[invite.id]:
                message += f" Invited by **{invite.inviter.display_name}** from **{invite.code}**"
                query = ''' SELECT location FROM invites WHERE id=%s '''
                params = (str(invite.id),)
                CURSOR.execute(query, params)
                loc = CURSOR.fetchone()
                if loc[0] is not "0":
                    message += f", located at **{str(loc[0])}**"
                break

        await self.cache_invites(await self.BOT.get_guild(GUILD_ID).invites())

        CURSOR.execute(''' SELECT value FROM defaults WHERE name=%s ''', ("invite",))
        value = CURSOR.fetchone()
        channel_id = int(value[0])
        if channel_id:
            await self.BOT.get_channel(channel_id).send(message)
        # else:
            # TODO: make bot dm me if this messes up


    # invite creation
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        CACHED_INVITE_LIST[invite.id] = 0
        data_string = str((invite.id,0))
        entry_string = f"INSERT INTO invites VALUES {data_string}"
        CURSOR.execute(entry_string)
        CONNECTION.commit()
        
        CURSOR.execute(''' SELECT value FROM defaults WHERE name=%s ''', ("invite",))
        value = CURSOR.fetchone()
        channel_id = int(value[0])
        if channel_id:
            await self.BOT.get_channel(channel_id).send(
                f"Invite **{invite.id}** has been created by **{invite.inviter}**")
        # else:
            # TODO: make bot dm me if this messes up

    # update invite command
    @commands.command()
    async def update(ctx, invite_id, *, location):
        params = (str(location), str(invite_id))
        query = ''' UPDATE invites SET location=%s WHERE id=%s '''
        CURSOR.execute(query, params)
        if CURSOR.rowcount < 1:
            await ctx.send(f"I couldn't find **{invite_id}** in my invites database :c")
        else:
            await ctx.send(f"The new location of **{invite_id}** is now **{location}**")
        CONNECTION.commit()


    # fetch invite info
    @commands.command()
    async def getinfo(ctx, invite_id):
        query = ''' SELECT location FROM invites WHERE id=%s '''
        params = (str(invite_id),)
        CURSOR.execute(query, params)
        message = f"I couldn't find **{invite_id}** in my invites database :c"
        loc = CURSOR.fetchone()
        if loc[0] is not "0":
            message = f"The location of **{invite_id}** is **{loc[0]}**"
        await ctx.send(message)