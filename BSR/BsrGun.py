import random
import copy

# 空包
BLANK = 0
# 実包
AMM = 1

# 弾丸リスト
BULLETS_LIST = [
    [BLANK,AMM],
    [BLANK,BLANK,AMM],
    [BLANK,BLANK,BLANK,AMM],
    [BLANK,BLANK,AMM,AMM],
    [BLANK,BLANK,BLANK,AMM,AMM],
    [BLANK,BLANK,AMM,AMM,AMM],
    [BLANK,BLANK,BLANK,BLANK,AMM,AMM],
    [BLANK,BLANK,BLANK,AMM,AMM,AMM],
    [BLANK,BLANK,AMM,AMM,AMM,AMM]
]

class Gun:
    """銃クラス
    """
    def __init__(self)->None:
        """初期マガジンを弾丸リストからランダムに選択しシャッフルしてセットする。

        シャッフルする前の初期弾丸はinitBullで取得できる。
        """
        self.bullets = copy.deepcopy(BULLETS_LIST[random.randint(0, len(BULLETS_LIST)-1)])
        self.initBull = copy.deepcopy(self.bullets)
        random.shuffle(self.bullets)
        self.damMul = False

    def setDamMul(self) -> None:
        """ダメージ2倍フラグを設定する。
        """
        self.damMul=True

    def unsetDamMul(self) -> None:
        """ダメージ2倍フラグを解除する。
        """
        self.damMul=False

    def bang(self) -> int:
        """銃弾を発砲する。

        Returns:
            int: 弾丸の種類
        """
        return self.bullets.pop(0)

    def getNext(self) -> int:
        """次の弾丸情報を取得する。

        Returns:
            int: 弾丸の種類
        """
        return self.bullets[0]

    def getNumOfBul(self) -> int:
        """残りの弾数を取得する。

        Returns:
            int: 残弾数
        """
        return len(self.bullets)