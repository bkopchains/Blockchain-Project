from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import binascii
from blockchain_constants import *
import sys, time


class Message:
    def __init__(self, msg_str):
        self.msg_str = msg_str
        self.pub_key = binascii.unhexlify(msg_str.split("&")[0])
        self.type = len((msg_str.split("&")[1]).split(":"))
        self.msg_body = binascii.unhexlify(msg_str.split("&")[1].split(":")[1])
        self.digital_sig = binascii.unhexlify(msg_str.split("&")[2])
        self.timestamp = str(time.time()).encode()
        self.recipient_key = None
        if self.type == MESSAGE_PRIVATE:
            self.recipient_key = binascii.unhexlify(msg_str.split("&")[1].split(":")[2])

    def print(self):
        print("MSG_TYPE: ", self.type)
        print(self.pub_key)
        print("MSG_BODY: ", self.msg_body)
        print("MSG_TIMESTAMP: ", self.timestamp)
        # print("SIGNATURE: ",self.digital_sig)
        pubkey = serialization.load_pem_public_key(self.pub_key, backend=default_backend())
        print(pubkey.verify(
            self.digital_sig,
            self.msg_body,
            padding.PSS(
                mgf = padding.MGF1(hashes.SHA256()),
                salt_length = padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        ))







