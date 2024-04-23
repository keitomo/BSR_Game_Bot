class Player:
    def __init__(self,health:int,userInfo: str,itemNum:int ) -> None:
        self.health = health
        self.items = []
        self.skip = False
        self.userInfo = userInfo
        self.itemNum = itemNum
        self.mention = userInfo.mention
        self.id = userInfo.id
        self.name = userInfo.name

    def addItem(self,item) -> None:
        if len(self.items) < self.itemNum:
            self.items.append(item)

    def useItem(self,item,player2:'Player',gun) -> tuple:
        for i in self.items:
            if i.id == item:
                item = i
        itemIndex = self.items.index(item)
        usedItem = self.items.pop(itemIndex)
        return usedItem.use(self,player2,gun)

    def setSkip(self) -> None:
        self.skip=True

    def unsetSkip(self) -> None:
        self.skip=False

    def damage(self,point:int) -> bool:
        self.health -= point
        if self.health <= 0:
            return True
        else:
            return False

    def heal(self,point:int) -> None:
        self.health += point

