import random

count = {
    "Beer": 0,
    "MagnifyingGlass": 0,
    "Cigarette": 0,
    "Handcuffs": 0,
    "Saw": 0,
    "Whiskey": 0
}

ITEM_PROB = {
    "Beer": 19,
    "MagnifyingGlass": 19,
    "Cigarette": 19,
    "Handcuffs": 19,
    "Saw": 19,
    "Whiskey": 5
}

numOfAttempts = 10000000

def chooseItemByProbability(probabilities):
    x = random.randint(1, 100)
    cumulative_prob = 0
    for item, prob in probabilities.items():
        cumulative_prob += prob
        if x <= cumulative_prob:
            return item

for _ in range(numOfAttempts):
    count[chooseItemByProbability(ITEM_PROB)]+=1

for key, value in count.items():
    print(f"アイテム {key} 確率: {(value/numOfAttempts)*100}%")
