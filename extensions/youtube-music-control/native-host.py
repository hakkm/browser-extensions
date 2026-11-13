#!/usr/bin/python3
"""Bridge a GNOME shortcut to the YouTube Music extension without network access."""
import json
import os
import select
import shutil
import socket
import stat
import struct
import subprocess
import sys
from pathlib import Path


def socket_path():
    runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))
    directory = runtime / 'youtube-music-control'
    directory.mkdir(mode=0o700, exist_ok=True)
    metadata = directory.lstat()
    if metadata.st_uid != os.getuid() or not stat.S_ISDIR(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o700:
        raise RuntimeError('YouTube Music runtime directory must be private and owned by you')
    return directory / 'control.sock'


def read_exact(stream, length):
    result = bytearray()
    while len(result) < length:
        chunk = stream.read(length - len(result))
        if not chunk:
            raise EOFError('Browser connection closed')
        result.extend(chunk)
    return bytes(result)


def read_message(stream):
    length = struct.unpack('=I', read_exact(stream, 4))[0]
    if length > 65536:
        raise ValueError('Native message is too large')
    return json.loads(read_exact(stream, length))


def write_message(stream, message):
    body = json.dumps(message).encode()
    stream.write(struct.pack('=I', len(body)) + body)
    stream.flush()


def serve():
    path = socket_path()
    if path.exists():
        with socket.socket(socket.AF_UNIX) as probe:
            try:
                probe.connect(str(path))
            except ConnectionRefusedError:
                path.unlink()
            else:
                raise RuntimeError('Another Brave profile already controls YouTube Music')
    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(path))
        server.listen(4)
        try:
            while True:
                ready, _, _ = select.select([server, sys.stdin.buffer], [], [])
                if sys.stdin.buffer in ready:
                    read_message(sys.stdin.buffer)
                if server not in ready:
                    continue
                with server.accept()[0] as client:
                    client.settimeout(5)
                    if client.recv(1) != b't':
                        continue
                    write_message(sys.stdout.buffer, {'action': 'toggle'})
                    if not select.select([sys.stdin.buffer], [], [], 4)[0]:
                        raise TimeoutError('YouTube Music extension did not respond')
                    reply = read_message(sys.stdin.buffer)
                    try:
                        client.sendall(json.dumps(reply).encode())
                    except BrokenPipeError:
                        pass
        finally:
            path.unlink(missing_ok=True)


def toggle():
    try:
        with socket.socket(socket.AF_UNIX) as client:
            client.settimeout(5)
            client.connect(str(socket_path()))
            client.sendall(b't')
            response = bytearray()
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                response.extend(chunk)
                if len(response) > 65536:
                    raise ValueError('Native reply is too large')
            reply = json.loads(response)
            if not reply.get('ok'):
                raise RuntimeError(reply.get('error', 'Cannot control YouTube Music'))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        message = str(error)
        if isinstance(error, (FileNotFoundError, ConnectionRefusedError)):
            message = 'Load or reload YouTube Music Only in Brave, then try Win+Shift+K again.'
        print(message, file=sys.stderr)
        if shutil.which('notify-send'):
            subprocess.run(['notify-send', 'YouTube Music', message], check=False)
        return 1


if __name__ == '__main__':
    if sys.argv[1:] == ['--toggle']:
        raise SystemExit(toggle())
    try:
        serve()
    except EOFError:
        pass
    except (OSError, ValueError, RuntimeError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
