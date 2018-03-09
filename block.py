import random,binascii
class Block:
    def __init__(self):
        self.nonce;


    def generate_nonce(length=64):
        return binascii.hexlify(random.random(length))
