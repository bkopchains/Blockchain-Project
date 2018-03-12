import random, binascii

class Block:
    def __init__(self, block_str):
        self.nonce = binascii.unhexlify(block_str.split("|")[0])
        self.parent = binascii.unhexlify(block_str.split("|")[1])
        self.timestamp=binascii.unhexlify(block_str.split("|")[2])
        self.nonce = self.generateNonce();
        self.parentNode = None;

    # returns a hexlified random 64 bit nonce
    def generateNonce(self):
        return binascii.hexlify(str(random.getrandbits(64)).encode())

    def print(self):
        print(self.nonce)
    
    #returns True if hash is verified to be true, false otherwise
    def verify(self):
        parentSplit = self.parent.split()
        zeroCount = 0
        for letter in parentSplit:
            if letter == "0":
                zeroCount+=1
        if zeroCount >= 5:
            return True
        else:
            return False

testblock = Block()
testblock.generateNonce()
testblock.print()

