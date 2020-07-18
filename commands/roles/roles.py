import discord
from discord.ext import commands

default_channel = 0
cache_roles = []


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # EMOIF=ROLE_ID

    def cache_roles():
        f = open("roles.txt", "r")
        lines = f.readlines()
        for line in lines:
            line_list = line.split("=")
            cached_roles.append(line_list)

    # set channel command

    @commands.command()
    async def setchannel(self, ctx):
        global default_channel
        default_channel = ctx.message.channel
        await ctx.send(f"#{default_channel} has been set as the default channel"
                       + " for role reactions!")

    # role message function

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
