from binascii import hexlify
import time
import os
import random

_id_ord = random.randint(0, 0xffff)


def generate_id(e_type: int) -> str:
    global _id_ord
    _id_ord = (_id_ord + 1) % 0xffff
    return ''.join([
        hex(int(time.time()))[2:],
        hexlify(os.urandom(2)).decode('utf-8'),
        hex(_id_ord)[2:].rjust(2, '0')[:4],
        hex(e_type)[2:].rjust(2, '0')[:2]
    ])
