import discord
from discord.ui import Button,View,Select
import random
import asyncio
from functools import wraps
from BSR.BsrCore import BSRGame
from BSR.BsrItem import *
from BSR.BsrPlayer import Player
from BSR.BsrGun import Gun,BLANK,AMM

NO_TURN_NOTIF = {"content":"あなたのターンではないです","ephemeral":True,"delete_after":8}
HEART = "\N{Heavy Black Heart}"


def defer_interaction_response(func):
    """すべてのインタラクションのデコレータ
    """
    @wraps(func)
    async def wrapper(interaction, *args, **kwargs):
        # 元の関数を実行
        await func(interaction, *args, **kwargs)
        # 最後にdeferを呼び出す
        if not interaction.response.is_done():
            await interaction.response.defer()
    return wrapper

async def startRound(game,interaction,reloadFlg=False):
    if reloadFlg:
        initBull = game.reload()
    else:
        initBull = game.startRound()
    random.shuffle(initBull)
    content = "以下の弾丸がランダムに込められます\n"
    for b in initBull:
        if b == BLANK:
            content+="\N{Large Blue Square}"
        elif b == AMM:
            content+="\N{Large Red Square}"
    await interaction.message.edit(content=content)
    await asyncio.sleep(3)
    await interaction.message.edit(content="")

async def updGameAndStartRound(game, interaction,reloadFlg=False):
    await interaction.response.defer()
    # ゲームのEmbedとViewを更新
    _embed, _view = await gameEmbed(game,True)
    await interaction.message.edit(embed=_embed, view=_view)
    # 新しいラウンドを開始
    await startRound(game, interaction,reloadFlg)
    # 再度ゲームのEmbedとViewを更新
    _embed, _view = await gameEmbed(game)
    await interaction.message.edit(embed=_embed, view=_view)

def crePlFld(players):
    """プレイヤー一覧文字列を作成する関数

    Args:
        players (list): 参加プレイヤー一覧

    Returns:
        str: プレイヤー一覧文字列
    """
    result = ""
    for p in players:
        result += p.mention
        result += " \n"
    if result == "":
        return "だれもいません"
    else:
        return result


async def mainEmbed(game:BSRGame):
    """メイン(最初)の埋め込みを作成する関数

    Args:
        game (BSRGame): ゲームオブジェクト

    Returns:
        tuple: embedとviewのタプル
    """
    embed = discord.Embed(title="BSRゲーム参加", description="以下の状況でゲームを開始します。", color=0x00ff00)
    embed.add_field(name="参加者",value=crePlFld(game.getPlayer()))

    # 参加者が二人になるまでスタートは押せない
    joinBtnFlg = False if len(game.getPlayer())<2 else True
    startBtnFlg = not joinBtnFlg

    # 各種ボタン生成
    joinBtn = Button(label="参加する",style=discord.ButtonStyle.green,emoji="\N{Raised Back of Hand}",disabled=joinBtnFlg)
    leaveBtn = Button(label="退出する",style=discord.ButtonStyle.blurple,emoji="\N{Waving Hand Sign}")
    startBtn= Button(label="開始する",style=discord.ButtonStyle.green,emoji="\N{Door}",disabled=(startBtnFlg))
    endBtn= Button(label="終了する",style=discord.ButtonStyle.red,emoji="\N{Collision Symbol}")

    # ボタン押下時の処理関数
    @defer_interaction_response
    async def join(interaction):
        game.addPlayer(interaction.user)
        _embed,_view = await mainEmbed(game)
        await interaction.message.edit(embed=_embed,view=_view)

    @defer_interaction_response
    async def leave(interaction):
        game.subPlayer(interaction.user)
        _embed,_view = await mainEmbed(game)
        await interaction.message.edit(embed=_embed,view=_view)

    @defer_interaction_response
    async def start(interaction):
        _embed,_ = await mainEmbed(game)
        await interaction.message.edit(embed=_embed,view=View(timeout=600.0))
        _embed,_view = await firstEmbed(game)
        await interaction.message.edit(embed=_embed,view=_view)

    @defer_interaction_response
    async def end(interaction):
        _embed=discord.Embed(title="BSRゲーム",description="ゲームを終了しました。")
        await interaction.message.edit(embed=_embed,view=View(timeout=600.0))

    # ボタンを追加
    view=View(timeout=600.0)
    view.add_item(joinBtn)
    view.add_item(leaveBtn)
    view.add_item(startBtn)
    view.add_item(endBtn)

    # ボタン押下時の関数指定
    joinBtn.callback = join
    leaveBtn.callback = leave
    startBtn.callback= start
    endBtn.callback = end

    return embed,view

async def firstEmbed(game:BSRGame):
    # ゲーム開始前に、だれを先攻にするか、ランダムにするかの設定をする。
    embed = discord.Embed(title="BSRゲーム", description="初期設定", color=0xff0000)
    embed.add_field(name="参加者",value=crePlFld(game.getPlayer()))
    embed.add_field(name="体力",value=game.health)
    embed.add_field(name="最大アイテム数",value=game.itemNum)
    embed.add_field(name="ラウンド数",value=game.maxRound)
    firstBtn = Button(label=game.getPlayer(0).userInfo.name+"を先攻で始める",style=discord.ButtonStyle.gray)
    secondBtn = Button(label=game.getPlayer(1).userInfo.name+"を先攻で始める",style=discord.ButtonStyle.gray)
    thirdBtn = Button(label="先攻をランダムで決める",style=discord.ButtonStyle.gray)
    endBtn= Button(label="終了する",style=discord.ButtonStyle.red,emoji="\N{Collision Symbol}")

    @defer_interaction_response
    async def first(interaction):
        game.setTurnPlayer(game.getPlayer(0).id)
        await updGameAndStartRound(game, interaction)

    @defer_interaction_response
    async def second(interaction):
        game.setTurnPlayer(game.getPlayer(1).id)
        await updGameAndStartRound(game, interaction)

    @defer_interaction_response
    async def third(interaction):
        i = random.randint(0,1)
        game.setTurnPlayer(game.getPlayer(i).id)
        await updGameAndStartRound(game, interaction)

    @defer_interaction_response
    async def end(interaction):
        _embed=discord.Embed(title="BSRゲーム",description="ゲームを終了しました。")
        await interaction.message.edit(embed=_embed,view=View(timeout=600.0))

    view=View(timeout=600.0)
    view.add_item(firstBtn)
    view.add_item(secondBtn)
    view.add_item(thirdBtn)
    view.add_item(endBtn)

    firstBtn.callback = first
    secondBtn.callback = second
    thirdBtn.callback = third
    endBtn.callback = end
    return embed,view

async def gameEmbed(game:BSRGame,btnFlg=False):
    embed = discord.Embed(title="BSRゲーム", description="現在の状況", color=0xff0000)
    embed.add_field(name="ラウンド",value=str(game.round)+"/"+str(game.maxRound),inline=True)
    embed.add_field(name="現在のターン",value=game.getTurnPlayer().mention,inline=True)
    if game.logText != None:
        embed.add_field(name="ゲームログ",value=game.logText,inline=False)
    for i in range(len(game.players)):
        wins = game.wins.get(game.getPlayer(i).id) if game.wins.get(game.getPlayer(i).id) is not None else 0
        embed.add_field(name="", value=game.getPlayer(i).mention+("\N{White Medium Star}"*wins),inline=False)
        embed.add_field(name="体力", value=HEART*game.getPlayer(i).health, inline=True)
        embed.add_field(name="アイテム数", value=str(len(game.getPlayer(i).items))+"/"+str(game.itemNum), inline=True)
        if i == 0:
            embed.add_field(name="\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_", value="",inline=False)

    itemFlg = len(game.getTurnPlayer().items)==0
    itemViewFlg = len(game.getTurnPlayer().items)==0 and len(game.getTurnEnemy().items)==0
    iamBtn = Button(label="自分を撃つ",style=discord.ButtonStyle.red,disabled=btnFlg)
    youBtn = Button(label="相手を撃つ",style=discord.ButtonStyle.red,disabled=btnFlg)
    itmBtn= Button(label="アイテムを使う",style=discord.ButtonStyle.gray,disabled=(itemFlg or btnFlg))
    itmViewBtn= Button(label="アイテムを見る",style=discord.ButtonStyle.gray,disabled=(itemViewFlg or btnFlg))

    async def responseProcess(response,game,interaction):
        if response=="reload":
            await updGameAndStartRound(game, interaction, True)
        elif response=="startRound":
            await updGameAndStartRound(game, interaction)
        elif response=="endGame":
            _embed,_view = await endEmbed(game)
            await interaction.message.edit(embed=_embed,view=_view)
        else:
            _embed, _view = await gameEmbed(game)
            await interaction.message.edit(embed=_embed, view=_view)

    @defer_interaction_response
    async def iam(interaction):
        if interaction.user.id == game.turnPlayerId:
            target =  game.getTurnPlayer().id
            response = game.bang(target)
            await responseProcess(response,game,interaction)
        else:
            await interaction.response.send_message(**NO_TURN_NOTIF)

    @defer_interaction_response
    async def you(interaction):
        if interaction.user.id == game.turnPlayerId:
            target = game.getTurnEnemy().id
            response = game.bang(target)
            await responseProcess(response,game,interaction)
        else:
            await interaction.response.send_message(**NO_TURN_NOTIF)

    @defer_interaction_response
    async def item(interaction):
        if interaction.user.id == game.turnPlayerId:
            _view = await itemSelect(game)
            await interaction.message.edit(view=_view)
        else:
            await interaction.response.send_message(**NO_TURN_NOTIF)

    @defer_interaction_response
    async def itemView(interaction):
        if interaction.user.id == game.turnPlayerId:
            _embed,_view = await itemViewEmbed(game)
            await interaction.message.edit(embed=_embed,view=_view)
        else:
            await interaction.response.send_message(**NO_TURN_NOTIF)

    view=View(timeout=600.0)
    view.add_item(iamBtn)
    view.add_item(youBtn)
    view.add_item(itmBtn)
    view.add_item(itmViewBtn)

    iamBtn.callback = iam
    youBtn.callback = you
    itmBtn.callback = item
    itmViewBtn.callback = itemView

    return embed,view

async def itemSelect(game:BSRGame):

    select = Select(placeholder="アイテムを選択してください")
    for n,i in enumerate(game.getTurnPlayer().items):
        select.add_option(label=i.name,value=i.id+"_"+str(n),description=i.description,emoji=i.emoji)

    backBtn = Button(label="戻る",style=discord.ButtonStyle.gray,emoji="\N{Leftwards Arrow with Hook}")

    @defer_interaction_response
    async def selectItem(interaction):
        if interaction.user.id == game.turnPlayerId:
            item = interaction.data.get("values")[0].split("_")[0]
            itemId ,result = game.useItem(item)
            if itemId == "Beer":
                if(game.gun.getNumOfBul()==0):
                    game.logText+="新しいマガジンがセットされた。\n"
                    game.changeTurn()
                    await updGameAndStartRound(game, interaction, True)
            elif itemId == "MagnifyingGlass":
                bull="\N{Large Red Square}" if result == AMM else "\N{Large Blue Square}"
                await interaction.response.send_message(content=f"次の弾丸は{bull}",ephemeral=True,delete_after=3)
            elif itemId == "Whiskey":
                await updGameAndStartRound(game, interaction, True)
            _embed, _view = await gameEmbed(game)
            await interaction.message.edit(embed=_embed, view=_view)
        else:
            await interaction.response.send_message(**NO_TURN_NOTIF)

    @defer_interaction_response
    async def back(interaction):
        _embed,_view = await gameEmbed(game)
        await interaction.message.edit(embed=_embed,view=_view)

    view=View(timeout=600.0)
    view.add_item(backBtn)
    view.add_item(select)

    select.callback = selectItem
    backBtn.callback = back

    return view

async def itemViewEmbed(game:BSRGame):
    embed = discord.Embed(title="BSRゲーム", description="所持アイテム一覧", color=0xff0000)
    for i in range(len(game.players)):
        items=""
        for item in game.getPlayer(i).items:
            items+="・"+item.name+"\n"
        if items=="":
            items="アイテムを持っていません"
        embed.add_field(name="", value=game.getPlayer(i).mention+"の所持アイテム",inline=False)
        embed.add_field(name="", value=items,inline=False)
        if i == 0:
            embed.add_field(name="\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_", value="",inline=False)
    backBtn = Button(label="戻る",style=discord.ButtonStyle.gray,emoji="\N{Leftwards Arrow with Hook}")

    @defer_interaction_response
    async def back(interaction):
        _embed,_view = await gameEmbed(game)
        await interaction.message.edit(embed=_embed,view=_view)

    view=View(timeout=600.0)
    view.add_item(backBtn)

    backBtn.callback = back

    return embed,view

async def endEmbed(game:BSRGame):
    embed = discord.Embed(title="BSRゲーム", color=0xff0000)
    embed.add_field(name="ゲーム終了",value="",inline=False)
    embed.add_field(name="優勝者",value=game.players.get(game.winnerId).mention,inline=False)

    view=View(timeout=600.0)

    return embed,view