import binascii
from blockchain_constants import *
import sys, time


class Message:
    def __init__(self, msg_str):
        self.msg_str=msg_str
        self.pub_key=binascii.unhexlify(msg_str.split("&")[0])
        self.type=len((msg_str.split("&")[1]).split(":"))
        self.msg_body=binascii.unhexlify(msg_str.split("&")[1].split(":")[1])
        self.digital_sig=self.pub_key=binascii.unhexlify(msg_str.split("&")[2])
        self.timestamp = str(time.time()).encode()
        self.recipient_key=None
        if (self.type==MESSAGE_PRIVATE):
            self.recipient_key=binascii.unhexlify(msg_str.split("&")[1].split(":")[2])

    def print(self):
        print(self.type)
        print(self.pub_key)
        print(self.msg_body)
        print(self.digital_sig)







