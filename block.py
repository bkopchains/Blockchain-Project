import random, binascii

class Block:
    def __init__(self):
        self.nonce = self.generateNonce();
#        self.parentNode;


    def generateNonce(self):
        return  binascii.hexlify(str(random.getrandbits(64)).encode())

    def print(self):
        print(self.nonce)

testblock = Block()
testblock.generateNonce()
testblock.print()

