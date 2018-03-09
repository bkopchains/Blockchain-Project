import random

class Block:
    def __init__(self):
        self.nonce = None;
        self.parentNode;


    def generateNonce(self):
        nonce = random.randint(1, 100000)
        print(nonce)


testblock = Block()
testblock.generateNonce()
