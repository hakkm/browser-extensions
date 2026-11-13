#!/usr/bin/python3
import argparse
import json
import os
import select
import socket
import stat
import sys
from pathlib import Path

from host import receive, send


def socket_path():
    runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))
    directory = runtime / 'native-messaging-demo'
    directory.mkdir(mode=0o700, exist_ok=True)
    metadata = directory.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o700:
        raise RuntimeError('Demo socket directory must be private and owned by you')
    return directory / 'control.sock'


def serve():
    path = socket_path()
    if path.exists():
        with socket.socket(socket.AF_UNIX) as probe:
            try:
                probe.connect(str(path))
            except ConnectionRefusedError:
                path.unlink()
            else:
                raise RuntimeError('The demo helper is already running in another connection')
    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(path))
        server.listen(4)
        try:
            while True:
                ready, _, _ = select.select([server, sys.stdin.buffer], [], [])
                if sys.stdin.buffer in ready:
                    if receive() is None:
                        return
                if server not in ready:
                    continue
                with server.accept()[0] as client:
                    client.settimeout(5)
                    if client.recv(1) != b't':
                        continue
                    send({'action': 'toggle'})
                    if not select.select([sys.stdin.buffer], [], [], 4)[0]:
                        raise TimeoutError('Browser extension did not reply')
                    reply = receive()
                    if reply is None:
                        raise EOFError('Browser disconnected')
                    try:
                        client.sendall(json.dumps(reply).encode('utf-8'))
                    except BrokenPipeError:
                        pass
        finally:
            path.unlink(missing_ok=True)


def trigger():
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
                raise ValueError('Reply is too large')
    print('Extension replied:', json.loads(response))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Demo browser bridge and shortcut sender')
    parser.add_argument('--toggle', action='store_true', help='Send one request to the running bridge')
    args = parser.parse_args()
    try:
        if args.toggle:
            trigger()
        else:
            serve()
    except (OSError, ValueError, RuntimeError, EOFError) as error:
        print(f'{error}. Register the helper and load/reload Communication Demo in Brave.', file=sys.stderr)
        raise SystemExit(1)
