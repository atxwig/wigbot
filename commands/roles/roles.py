import discord
from discord.ext import commands
from emoji import UNICODE_EMOJI
import sqlite3

default_channel_id = 0

cache_roles = []


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # # MESSAGE_ID:EMOJI=ROLE_ID,EMOJI=ROLE_ID...
    # def cache_roles():
    #     f = open("roles.txt", "r")
    #     lines = f.readlines()
    #     for line in lines:
    #         line_list = line.split(":")
    #         cached_roles.append(line_list)


    # set channel command
    @commands.command()
    async def setroleschannel(self, ctx):
        global default_channel_id
        default_channel_id = ctx.message.channel.id
        await ctx.send(f"{self.bot.get_channel(default_channel_id).mention} has been set as the default channel" 
                         + " for role reactions! [LOCAL]")


    # get channel command
    @commands.command()
    async def getroleschannel(self, ctx):
        global default_channel_id
        await ctx.send(f"The default channel is {self.bot.get_channel(default_channel_id).mention}.")

    # send role message function
    @commands.command()
    async def sendrolemessage(self, ctx):
        error_message = []
        message_list  = []
        content       = ctx.message.content[17:]
        content_list  = content.split("-")

        message_list.append(content_list[0])

        for message in content_list[1:]:
            message_pair = message.split(" ")

            if message_pair[0] in UNICODE_EMOJI:
                role_id = int(message_pair[1][3:-1])
                role    = self.bot.get_guild(670469511572488223).get_role(role_id)
                
                if role is not None:
                    message_pair[1] = role.name
                    message_list.append(message_pair)

                else:
                    error_message.append(f"I don't know what role {message_pair[1]} is :c")
            else:
                error_message.append(f"I don't know what emoji {message_pair[0]} is :c")

        formatted_message = f"**{message_list[0]}**\n>>> "
        for role in message_list[1:]:
            formatted_message += f"{role[0]}  {role[1]}\n"

        await self.bot.get_channel(default_channel_id).send(formatted_message)

        if len(error_message) > 0:
            for error in error_message:
                await self.bot.get_channel(default_channel_id).send(error) 
    
    

    

    # select role message function


    # add role function

    
    # remove role function

    
    # assign / remove role on react


    # # hug command
    # @commands.command()
    # async def hug(self, ctx, member_id):
    #     member_id = member_id[3:-1]
    #     member = ctx.message.guild.get_member(int(member_id))
    #     if member:
    #         await ctx.send(f"{ctx.message.author.mention} is omega cute and " +
    #                         "hugged {member.mention}!")
    #     else:
    #         await ctx.send("I couldn't find that user D:")
