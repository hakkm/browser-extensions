#!/usr/bin/env python3
"""List unpacked browser extensions without maintaining a second registry."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'extensions'
failed = False
for path in sorted(root.rglob('manifest.json')):
    if any(part.startswith('.') or part in {'node_modules', '__pycache__'}
           for part in path.relative_to(root).parts):
        continue
    try:
        manifest = json.loads(path.read_text())
        if 'manifest_version' not in manifest:
            continue
        print(f"{manifest['name']} ({manifest['version']})")
        print(f"  Load unpacked: {path.parent}")
    except (OSError, ValueError, KeyError) as error:
        print(f'Invalid manifest: {path}: {error}')
        failed = True
raise SystemExit(1 if failed else 0)
