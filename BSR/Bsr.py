from discord.ext import commands
from discord.commands import SlashCommandGroup
from dotenv import load_dotenv
import os
from BSR.BsrCore import BSRGame
import BSR.BsrEmbed as createEmbed

load_dotenv()

guildId=int(os.getenv('GUILD_ID'))
health = int(os.getenv('HEALTH'))
maxRound = int(os.getenv('MAX_ROUND'))
itemNum = int(os.getenv('ITEM_NUM'))

class BSR(commands.Cog,name="bsr"):
    def __init__(self,bot):
        self.bot = bot

    wwg = SlashCommandGroup("bsr", "bsrゲームに関連するコマンド",guild_id=[guildId])

    @wwg.command(name="start",description="bsrゲームを開始します",guild_id=[guildId])
    async def start(self,ctx):
        game = BSRGame(health=health,itemNum=itemNum,maxRound=maxRound,roundItemNum=3)
        embed,view = await createEmbed.mainEmbed(game)
        await ctx.respond(embed=embed,view=view)

def setup(bot):
    bot.add_cog(BSR(bot))
