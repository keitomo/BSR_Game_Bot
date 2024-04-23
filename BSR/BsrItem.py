class Item:
    """アイテムの基底クラス

    アイテムを追加する際はこのクラスを継承すること
    """
    def __init__(self,id,name,emoji,description):
        self.id = id
        self.name = name
        self.emoji = emoji
        self.description = description
    def use(self,player1,player2,gun) -> tuple:
        return (None,None)

# アイテムごとの確率設定
# id:確率の形で明記
ITEM_PROB = {
    "Beer": 19,
    "MagnifyingGlass": 19,
    "Cigarette": 19,
    "Handcuffs": 19,
    "Saw": 19,
    "Whiskey": 5
}

# ビール
class Beer(Item):
    def __init__(self):
        super().__init__("Beer","ビール", "\N{BEER MUG}","弾丸を1つ排莢する")

    def use(self,player1,player2,gun) -> tuple:
        return ("Beer",gun.bang())

# 虫眼鏡
class MagnifyingGlass(Item):
    def __init__(self):
        super().__init__("MagnifyingGlass","虫眼鏡", "\N{LEFT-POINTING MAGNIFYING GLASS}","次の弾丸を確認する")

    def use(self,player1,player2,gun) -> tuple:
        return ("MagnifyingGlass",gun.getNext())

# 煙草
class Cigarette(Item):
    def __init__(self):
        super().__init__("Cigarette","煙草", "\N{SMOKING SYMBOL}","体力を1回復する")

    def use(self,player1,player2,gun) -> tuple:
        player1.heal(1)
        return ("Cigarette",True)

# 手錠
class Handcuffs(Item):
    def __init__(self):
        super().__init__("Handcuffs","手錠", "\N{CHAINS}","相手のターンを一度だけスキップする")

    def use(self,player1,player2,gun) -> tuple:
        player2.setSkip()
        return ("Handcuffs",True)

# のこぎり
class Saw(Item):
    def __init__(self):
        super().__init__("Saw","のこぎり", "\N{CARPENTRY SAW}","発砲時のダメージを2倍にする")

    def use(self,player1,player2,gun) -> tuple:
        gun.setDamMul()
        return ("Saw",True)

# ウィスキー
class Whiskey(Item):
    def __init__(self):
        super().__init__("Whiskey","ウィスキー", "\N{TUMBLER GLASS}","銃をリセットする")

    def use(self,player1,player2,gun) -> tuple:
        return ("Whiskey",None)