import random, binascii
from blockchain_constants import *
import time
import hashlib

class Block:

    # multiple methods of constructing the block object based on what is given
    def __init__(self, block_str = None, msgs_str = None, parent = None):
        # given a full block string
        if block_str is not None and msgs_str is None:
            self.nonce = block_str.split("|")[0]
            self.parent = block_str.split("|")[1]
            self.miner_ID = block_str.split("|")[2]
            self.timestamp = block_str.split("|")[3]
            self.msgs = "|".join(block_str.split("|")[4:])
        # given a list of messages and a parent block
        elif block_str is None and msgs_str is not None and parent is not None:
            self.parent = parent
            self.valid = False
        # given nothing or some other combination
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
    def verify(self, parent):
        zeroCount = 0
        for letter in self.parent[:5]:
            if letter == "0":
                zeroCount += 1
        if zeroCount >= PROOF_OF_WORK_HARDNESS and parent.timestamp < self.timestamp:
            print("BLOCK ", self.timestamp, "VERIFIED")
            return True
        else:
            return False

    def tryMine(parent, minerID, msgs):

        mined = Block(msgs_str=msgs,parent=parent)
        mined.miner_ID = minerID
        mined.timestamp = str(time.time())
        msgs_enc = b''
        for msg in msgs:
            msgs_enc += b'|' + msg.encode()
        # (bwn_enc = block without nonce, encoded)
        bwn_enc = mined.parent + b'|' + mined.miner_ID.encode() + b'|' + mined.timestamp.encode() + msgs_enc
        while not mined.valid:
            mined.nonce = mined.generateNonce()
            tryblock = mined.nonce + b'|' + bwn_enc
            mined.parent = hashlib.sha512(tryblock).hexdigest()
            mined.valid = mined.verify()
        return mined
# testblock = Block()
# testblock.generateNonce()
# testblock.print()
