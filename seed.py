"""Seed a few cups of coffee.

Usage:
    python seed.py            # seeds the local `coffee` catalog directory
    python seed.py my_dir     # or another directory you passed to `pxt schema update`
"""
import sys
from pathlib import Path

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'coffee'
HERE = Path(__file__).resolve().parent

SEED = {
    'cups': [
        {'bean': 'Yirgacheffe', 'origin': 'Ethiopia', 'roast_level': 'light', 'rating': 5, 'notes': 'jasmine; bergamot; tea-like'},
        {'bean': 'Guji Natural', 'origin': 'Ethiopia', 'roast_level': 'City+', 'rating': 4, 'notes': 'blueberry; syrupy'},
        {'bean': 'Huila', 'origin': 'Colombia', 'roast_level': 'medium', 'rating': 4, 'notes': 'caramel; red apple'},
        {'bean': 'Sumatra Mandheling', 'origin': 'Indonesia', 'roast_level': 'french', 'rating': 3, 'notes': 'cedar; dark chocolate'},
    ],
}

for table_name, rows in SEED.items():
    t = pxt.get_table(f'{target}/{table_name}')
    if t.count() > 0:
        print(f'{target}/{table_name} already has {t.count()} rows; skipping')
        continue
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str) and v.startswith('data/'):
                row[k] = str(HERE / v)   # local sample media file
    t.insert(rows)
    print(f'inserted {len(rows)} rows into {target}/{table_name}')
