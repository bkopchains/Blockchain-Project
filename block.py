import random, binascii

class Block:
    def __init__(self):
        self.nonce = self.generateNonce();
        self.parentNode = None;


    def generateNonce(self):
        return  binascii.hexlify(str(random.getrandbits(64)).encode())

    def print(self):
        print(self.nonce)
    
    #returns True if hash is verified to be true, false otherwise
    def verify(self):
        return

testblock = Block()
testblock.generateNonce()
testblock.print()

