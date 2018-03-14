import queue
import threading
import binascii
from message import *
from block import *
from cryptography.hazmat.primitives.asymmetric import rsa
import os

import logging
import traceback, sys
from blockchain_constants import *

class Blockchain:

    '''Responsible for initializing a block chain object.  It currently
    takes no parameters, and does nothing, you'll want to change that.
    This object is created by blockchain_bbs.py.

    '''
    def __init__(self, keyfile):
        # Use this lock to protect internal data of this class from
        # the multi-threaded server.  Wrap code modifies the
        # blockchain in the context "with self.lock:".  Be careful not
        # to nest these contexts or it will cause deadlock.\
        kf = open(keyfile,"r")
        self.pub_key = kf.read().replace("\n","").encode()
        self.minerID = hashlib.sha256(self.pub_key).hexdigest()
        self.msglist = []

        #Similar log setup from network.py
        self.log = logging.getLogger('Mine')
        self.log.setLevel(logging.DEBUG)
        #file handler
        fh = logging.FileHandler('miner.log')
        fh.setLevel(logging.DEBUG)
        #console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        #formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        #add the handlers to the logger
        self.log.addHandler(fh)
        self.log.addHandler(ch)

        self.log.warning("=========== Miner function logging started ==========")

        self.lock = threading.Lock()
        self.msg_queue = queue.Queue()
        self.lockThread = threading.Lock()

        # handles filling ledger if text file is full or not
        ledger = open("ledger.txt", 'r')
        if os.stat("ledger.txt").st_size == 0:
            self.parent_node = None
            self.OG_block = None
        else:
            self.OG_block = Block(next(ledger).strip())
            self.parent_node = Block(ledger.readlines()[-1])

        # queue of blocks mined by our miner
        self.blocksMined = queue.Queue()
        self.allBlocks = []

        self.log.warning("=========== Miner init complete ==========")
        self.readable_messages = 0
        self.longest_chain = 0
        pass
        
    '''Returns the number of messages that are queued to be processed by
    the blockchain.  This function is called by networking.py.

    '''
    def get_message_queue_size(self):
        return self.msg_queue.qsize()
        
        
    '''Takes a string containing a message received by the server from a
    peer or a user.  The message may be illformed, a duplicate, or
    invalid.  If this is not the case, add it message to the queue of
    messages to be processed into the blockchain, and return True.
    Otherwise, return False.  This function is called by
    networking.py.

    '''
    def add_message_str(self, msg_str):
        # for item in msg_str.split("&"):
        #     print(item)
        msg = Message(msg_str)
        print(binascii.unhexlify(msg.msg_body.split(":")[1]))
        if not msg.illformed:
            if msg.verify():
                self.log.warning("=========== Message correctly formed and verified ==========")
            else:
                self.log.warning("=========== Message invalid - not verified ==========")
        else:
            self.log.warning("=========== Message ill-formed ==========")

        if msg not in self.msglist:
            self.log.warning("=========== Message not duplicate ==========")
            self.msglist.append(msg)
            self.msg_queue.put_nowait(msg)
        else:
            self.log.warning("=========== Message already in queue ==========")
        
        return False

    
    '''Takes a string containing a block received by the server from a
    peer or a user.  The block may be illformed, invalid, refer to
    non-existant previous block, or be a duplicate.  If this is not
    the case, add it to the blockchain and return True.  (This node's
    mining may be interrupted, if this new block supercedes the
    current block.)  Otherwise, return False.  This function is called
    by networking.py.

    '''
    def add_block_str(self, block_str):
        print("add_block_str(%s)" % block_str)
        tempblock = Block(block_str=block_str)
        f = open("ledger.txt", 'a')
        with self.lockThread:
            if (self.OG_block is None):
                f.write(block_str + "\n")
                f.close()
                self.OG_block = tempblock
                self.parent_node = tempblock
                return True
            elif (tempblock.verify() and tempblock.timestamp > self.parent_node.timestamp):
                f.write(block_str + "\n")
                f.close()
                self.parent_node = tempblock
                return True
        return False


    '''Return the string encoding of a newly mined block if it exists, and
    otherwise returns None.  This function should return immediately
    and not wait for a block to be mined.  This function is called by
    networking.py.

    '''
    def get_new_block_str(self):
        #print("get_new_block_str()")
        if self.blocksMined.qsize() != 0:
            return self.blocksMined.get_nowait().print()
        else:
            return None


    '''Returns a list of the string encoding of each of the blocks in this
    blockchain, including ones not on the main chain, whose timestamp
    is greater then the parameter t.  This function is called by
    networking.py.

    '''
    def get_all_block_strs(self, timestamp):
        blockCount = 0
        toReturn = []
        for i in range(len(self.allBlocks)):
            if self.allBlocks[i].timestamp >= timestamp:
                blockCount+=1
                toReturn.append(self.allBlocks[i])
        for x in range(len(blockCount)):
            toReturn[x] = toReturn[x].encoded.decode()
        print("Total " + blockCount + " blocks ready to broadcast")
        return toReturn


    '''Waits for enough messages to be received from the server, forms
    them into blocks, mines the block, adds the block to the
    blockchain, and prepares the block to be broadcast by the server.
    The mining of a block may be interrupted by a superceding
    add_block_str() call.  In this case the miner should does its best
    to move on to mine another block and not lose any messages it was
    previous attempting to mine.  This process repeats forever, and
    this function never runs.  This function is called in
    blockchain_bbs.py as a new thread.

    '''

    def mine(self):

        self.log.warning("=========== Miner Initialized ==========")

        while True:
            self.writeToStats()
            msgs_toadd = []
            self.log.warning("=========== [Miner waiting for msgs] ==========")
            while MSGS_PER_BLOCK > len(msgs_toadd):
                msgs_toadd.append(self.msg_queue.get().msg_str)
            self.log.warning("=========== [Mining function started] ==========")

            # handles mining when there is no starting block
            if self.OG_block is None:
                tempBlock = Block.tryMine(b'000000000000000000000000000000000000', self.minerID, msgs_toadd)
                print("Gensis block mined!")
                self.blocksMined.put(tempBlock)
                self.allBlocks.append(tempBlock)
            # handles mining when given a parent block
            else:
                tempBlock = Block.tryMine(self.parent_node.parent.encode(), self.minerID, msgs_toadd)
                print("New block additional block mined!")
                self.blocksMined.put(tempBlock)
                self.allBlocks.append(tempBlock)


    #returns most recent block of longest chain
    def findLongestChain(self):
        parentHashes = []
        for block in self.allBlocks:
            parentHash = block.parent
            parentHashes.append(parentHash)
        #pseudo-code for how we would have liked to implement this function
        #1. check if any parents in parentHashes are the same
        #2. if any blocks are found to have the same parent hash, we know there is a split chain there
        #3. check the number of descending nodes from the two blocks that have the same parent hash
        #4. the one with more descending parents is the longest chain!
        #5. return most recent block of longest chain



    # Writes 4 lines to the stats file
    def writeToStats(self):
        f = open("ledger.txt", "r")
        f2 = open("stats.txt", "w")
        fh = f.read()
        blocks = fh.split('\n')
        for b in blocks:
            b.split("")
        numBlocks = len(blocks)-1
        f2.write("Number of blocks " + str(numBlocks) + '\n')

    def findLongestChain(self):
        return None
    
    def writeToMessages(self):
        return None
