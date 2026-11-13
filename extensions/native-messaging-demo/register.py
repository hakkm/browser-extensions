#!/usr/bin/python3
import argparse
import datetime
import json
import re
import shutil
import shlex
from pathlib import Path


parser = argparse.ArgumentParser(description='Register this demo helper with Brave on Linux.')
parser.add_argument('extension_id', help='ID shown on the Communication Demo extension card')
args = parser.parse_args()
if not re.fullmatch('[a-p]{32}', args.extension_id):
    parser.error('Expected a 32-character extension ID containing only a through p')

host = Path(__file__).resolve().parent / 'native-host.py'
host.chmod(host.stat().st_mode | 0o100)
target = Path.home() / '.config/BraveSoftware/Brave-Browser/NativeMessagingHosts/com.local.demo.json'
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists():
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    shutil.copy2(target, target.with_name(target.name + '.' + timestamp + '.backup'))
target.write_text(json.dumps({
    'name': 'com.local.demo',
    'description': 'Python communication demo',
    'path': str(host),
    'type': 'stdio',
    'allowed_origins': [f'chrome-extension://{args.extension_id}/'],
}, indent=2) + '\n')
print('Registered:', target)
print('Reload Communication Demo in brave://extensions, then inspect its service worker console.')
print('Test or use as a custom shortcut command:')
print(f'/usr/bin/python3 {shlex.quote(str(host))} --toggle')
