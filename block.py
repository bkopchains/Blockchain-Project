import random, binascii
from blockchain_constants import *

class Block:

    #multiple methods of constructing the block object based on what is given
    def __init__(self, block_str = None, msgs_str = None, parent = None):
        if block_str is not None and msgs_str is None:
            self.nonce = block_str.split("|")[0]
            self.parent = block_str.split("|")[1]
            self.miner_ID = block_str.split("|")[2]
            self.timestamp = block_str.split("|")[3]
            self.msgs = "|".join(block_str.split("|")[4:])
        elif block_str is None and msgs_str is not None and parent is not None:
            self.miner_ID = None
            self.parent = parent
            self.valid = False
        else:
            self.illformed = True
            self.valid = False


    # returns a hexlified random 64 bit nonce
    def generateNonce(self):
        return binascii.hexlify(str(random.getrandbits(64)).encode())

    # def print(self):
    #     if self.illformed is False:
    #         print("====== ILLFORMED BLOCK ======")
    #     else:
    #         print(self.nonce)
    
    # returns True if hash is verified to be true, false otherwise
    def verify(self):
        parentSplit = self.parent.split()
        zeroCount = 0
        for letter in parentSplit:
            if letter == "0":
                zeroCount+=1
        if zeroCount >= PROOF_OF_WORK_HARDNESS:
            return True
        else:
            return False

# testblock = Block()
# testblock.generateNonce()
# testblock.print()
