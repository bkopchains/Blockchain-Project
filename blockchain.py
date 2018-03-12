import queue
import threading
import binascii
from message import *
from block import *
from cryptography.hazmat.primitives.asymmetric import rsa

import logging
import traceback, sys
from blockchain_constants import *

class Blockchain:

    '''Responsible for initializing a block chain object.  It currently
    takes no parameters, and does nothing, you'll want to change that.
    This object is created by blockchain_bbs.py.

    '''
    def __init__(self):
        # Use this lock to protect internal data of this class from
        # the multi-threaded server.  Wrap code modifies the
        # blockchain in the context "with self.lock:".  Be careful not
        # to nest these contexts or it will cause deadlock.\

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

        self.parent_node = None
        self.OG_block = None
        self.minedBlock = None

        self.log.warning("=========== Miner init complete ==========")

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
        if tempblock.verify():
            f.write(block_str + "\n")
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
        return None


    '''Returns a list of the string encoding of each of the blocks in this
    blockchain, including ones not on the main chain, whose timestamp
    is greater then the parameter t.  This function is called by
    networking.py.

    '''
    def get_all_block_strs(self, t):

        return []


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
            msgs_toadd = []
            self.log.warning("=========== [Miner waiting for msgs] ==========")
            while MSGS_PER_BLOCK > msgs_toadd:
                msgs_toadd.append(self.msg_queue.get())
            self.log.warning("=========== [Mining function started] ==========")

            # if self.get_message_queue_size() == MSGS_PER_BLOCK:
            #     bstr = ""
            #     for i in range(0, self.get_message_queue_size()):
            #         bstr += (self.msg_queue.get_nowait().msg_body + "|")
            #     self.minedBlock = Block(msgs_str=bstr, parent=self.parent_node.parent)
            # pass
