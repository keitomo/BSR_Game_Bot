import discord
from discord.ext import commands
import random
import json

from BSR.BsrItem import *
from BSR.BsrPlayer import Player
from BSR.BsrGun import Gun,BLANK,AMM

class BSRGame:
    def __init__(self,health,itemNum,*,maxRound=3,roundItemNum=3):
        self.health=health
        self.itemNum = itemNum
        self.roundItemNum = roundItemNum
        self.players = {}
        self.wins = {}
        self.winnerId = None
        self.gun = None
        self.round = 0
        self.maxRound = maxRound
        self.turnPlayerId = None
        self.logText = None

    # ラウンド開始処理
    def startRound(self)->list:
        self.round += 1
        del self.gun
        self.gun = Gun()
        self.distItem()
        map(lambda x:x.unsetSkip(),self.players)
        self.gun.unsetDamMul()
        return self.gun.initBull

    def reload(self)->list:
        del self.gun
        self.gun = Gun()
        self.distItem()
        map(lambda x:x.unsetSkip(),self.players)
        self.gun.unsetDamMul()
        return self.gun.initBull

    # ラウンド終了処理
    def endRound(self):
        winPlayerId=None
        for p in self.players.values():
            if p.health != 0:
                winPlayerId = p.id
                break
        if self.wins.get(winPlayerId)!=None:
            self.wins[winPlayerId]+=1
        else:
            self.wins[winPlayerId]=1
        for id,win in self.wins.items():
            if win==int(self.maxRound/2)+1:
                return self.endGame(id)
        for p in self.players.values():
            p.unsetSkip()
            p.items = []
            p.health = self.health
            self.logText=None

    # ゲーム終了処理
    def endGame(self,id):
        self.winnerId = id
        return "endGame"

    # アイテムを配る
    def distItem(self) -> None:
        for _ in range(self.roundItemNum):
            for p in self.players.values():
                x = random.randint(1,100)
                cumulative_prob = 0
                sel_item = None
                for item, prob in ITEM_PROB.items():
                    cumulative_prob += prob
                    if x <= cumulative_prob:
                        sel_item = item
                        break
                if sel_item=="Beer":
                    item = Beer()
                elif sel_item=="MagnifyingGlass":
                    item = MagnifyingGlass()
                elif sel_item=="Cigarette":
                    item = Cigarette()
                elif sel_item=="Handcuffs":
                    item = Handcuffs()
                elif sel_item=="Saw":
                    item = Saw()
                elif sel_item=="Whiskey":
                    item = Whiskey()
                p.addItem(item)

    # プレイヤー追加
    def addPlayer(self,user):
        _player = Player(self.health,user,self.itemNum)
        if not user.id in self.players.keys():
            self.players[user.id] = _player

    # プレイヤー削除
    def subPlayer(self,user):
        if user.id in self.players.keys():
            del self.players[user.id]

    # プレイヤー取得
    def getPlayer(self,index = -1):
        if index == 0:
            return list(self.players.values())[0]
        elif index == 1:
            return list(self.players.values())[1]
        else:
            return self.players.values()

    # 現在のターンのプレイヤー設定
    def setTurnPlayer(self,turn):
        self.turnPlayerId = turn

    # 現在のターンのプレイヤー取得
    def getTurnPlayer(self):
        return self.players.get(self.turnPlayerId)

    # 現在の相手プレイヤー取得
    def getTurnEnemy(self):
        enemy = None
        for i in self.players.keys():
            if i != self.turnPlayerId:
                enemy = i
                break
        return self.players.get(enemy)

    def changeTurn(self):
        enemy = self.getTurnEnemy()
        self.setTurnPlayer(enemy.id)

    def useItem(self,item):
        itemId,result = self.getTurnPlayer().useItem(item,self.getTurnEnemy(),self.gun)
        if self.logText == None:
            self.logText = ""
        if itemId=="Beer":
            bull="\N{Large Red Square}" if result == AMM else "\N{Large Blue Square}"
            self.logText+=f"ビールを使用した。{bull}が排莢された。\n"
        elif itemId=="MagnifyingGlass":
            self.logText+=f"虫眼鏡を使用した。\n"
        elif itemId=="Cigarette":
            self.logText+=f"たばこを使用した。1回復した。\n"
        elif itemId=="Handcuffs":
            self.logText+=f"手錠を使用した。\n"
        elif itemId=="Saw":
            self.logText+=f"のこぎりを使用した。\n"
        elif itemId=="Whiskey":
            self.changeTurn()
            self.logText+=f"ウィスキーを使用した。新しいマガジンがセットされた。\n"
        return (itemId,result)

    # 発砲
    def bang(self,target_id):
        result = self.gun.bang()
        self.logText=""
        bull="\N{Large Red Square}" if result == AMM else "\N{Large Blue Square}"
        self.logText=f"{bull}が{self.players.get(target_id).mention}に発砲された。\n"
        skipCheckFlg = True
        chgTurnFlg = False
        bangResult = None
        if result == AMM:
            d=2 if self.gun.damMul else 1
            bangResult = self.players.get(target_id).damage(d)
        elif result == BLANK:
            if target_id == self.turnPlayerId:
                skipCheckFlg = False
        self.gun.unsetDamMul()
        if skipCheckFlg:
            enemy = self.getTurnEnemy()
            if not enemy.skip:
                if not chgTurnFlg:
                    chgTurnFlg = True
                    self.changeTurn()
            else:
                self.logText+=f"{enemy.mention}のターンはスキップされた。\n"
                enemy.unsetSkip()
        # どちらかの体力が0になったら
        if bangResult:
            res = self.endRound()
            if res == "endGame":
                return "endGame"
            if not chgTurnFlg:
                chgTurnFlg = True
                self.changeTurn()
            return "startRound"
        # マガジンが空だったら
        if(self.gun.getNumOfBul()==0):
            self.logText+="新しいマガジンがセットされた。\n"
            if not chgTurnFlg:
                chgTurnFlg = True
                self.changeTurn()
            return "reload"
