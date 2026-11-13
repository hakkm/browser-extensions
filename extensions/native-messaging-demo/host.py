#!/usr/bin/python3
import json
import struct
import sys


def read_exact(length):
    result = bytearray()
    while len(result) < length:
        chunk = sys.stdin.buffer.read(length - len(result))
        if not chunk:
            if not result:
                return None
            raise EOFError('Incomplete message')
        result.extend(chunk)
    return bytes(result)


def receive():
    header = read_exact(4)
    if header is None:
        return None
    length = struct.unpack('=I', header)[0]
    if length > 65536:
        raise ValueError('Message is too large')
    body = read_exact(length)
    if body is None:
        raise EOFError('Missing message body')
    return json.loads(body)


def send(message):
    body = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('=I', len(body)) + body)
    sys.stdout.buffer.flush()


if __name__ == '__main__':
    while True:
        message = receive()
        if message is None:
            break
        send({'ok': True, 'received': message})
