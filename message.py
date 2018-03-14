from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import binascii
from blockchain_constants import *
import sys, time


class Message:
    def __init__(self, msg_str):
        self.illformed = False
        self.valid = True
        self.msg_str = msg_str
        # setup message object given a full message string
        try:
            self.pub_key = binascii.unhexlify(msg_str.split("&")[0])
            self.type = len((msg_str.split("&")[1]).split(":"))
            self.msg_body = msg_str.split("&")[1]
            self.digital_sig = binascii.unhexlify(msg_str.split("&")[2])
            self.timestamp = self.msg_body.split(":")[0]
            self.recipient_key = None
            if self.type == MESSAGE_PRIVATE:
                self.recipient_key = binascii.unhexlify(msg_str.split("&")[1].split(":")[2])
        except:
            self.illformed = True

    def print(self):
        return self.msg_str

    # verifies a message by checking its digital signature with the public key
    def verify(self):
        backend = default_backend()
        pubkey = serialization.load_pem_public_key(self.pub_key, backend)
        try:
            # built-in verify function in public_key object
            pubkey.verify(
                self.digital_sig,
                self.msg_body.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            self.valid = False
            return False




