#!/usr/bin/env python3
"""Verify and extract the included multipart source-data archive. Standard library only."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    data = ROOT / 'data'
    manifest = json.loads((data / 'manifest.json').read_text())
    for part in manifest['parts']:
        path = data / part['file']
        if Path(part['file']).name != part['file'] or not path.is_file():
            raise ValueError('Missing or invalid archive part')
        if path.stat().st_size != part['bytes'] or sha256(path) != part['sha256']:
            raise ValueError(f'Archive part integrity check failed: {path.name}')
    with tempfile.TemporaryDirectory(prefix='yelp-data-') as temporary:
        archive = Path(temporary) / 'sources.zip'
        with archive.open('wb') as target:
            for part in manifest['parts']:
                with (data / part['file']).open('rb') as source:
                    shutil.copyfileobj(source, target)
        expected = {entry['file'] for entry in manifest['files']}
        with zipfile.ZipFile(archive) as bundle:
            if set(bundle.namelist()) != expected or len(bundle.namelist()) != len(expected):
                raise ValueError('Unexpected archive contents')
            for entry in manifest['files']:
                name = entry['file']
                if Path(name).name != name:
                    raise ValueError('Unsafe archive member')
                staged = Path(temporary) / name
                with bundle.open(name) as source, staged.open('wb') as target:
                    shutil.copyfileobj(source, target)
                if staged.stat().st_size != entry['bytes'] or sha256(staged) != entry['sha256']:
                    raise ValueError(f'Extracted file integrity check failed: {name}')
        # Validate every file before replacing any existing local source.
        for name in sorted(expected):
            shutil.copyfile(Path(temporary) / name, data / name)
            print(f'Extracted {name}')
    print('All parts and source files passed SHA-256 checks. Open the Tableau workbooks or run the data checks.')


if __name__ == '__main__':
    main()
