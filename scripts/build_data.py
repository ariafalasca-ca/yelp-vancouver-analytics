#!/usr/bin/env python3
"""Rebuild app aggregates from authorized course NDJSON. Python 3.10+, standard library."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
METRICS = ('useful', 'funny', 'cool', 'total')


def records(path):
    with path.open(encoding='utf-8-sig') as handle:
        for line_no, line in enumerate(handle, 1):
            if line.strip():
                try:
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError('expected an object')
                    yield row
                except (ValueError, TypeError) as exc:
                    raise ValueError(f'{path.name}, line {line_no}: {exc}') from exc


def integer(value):
    if isinstance(value, bool) or not re.fullmatch(r'\d+', str(value)):
        raise ValueError('expected a nonnegative integer')
    return int(value)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def stats(hist):
    n = sum(hist.values())
    def at(index):
        cumulative = 0
        for value, count in sorted(hist.items()):
            cumulative += count
            if cumulative > index:
                return value
    return dict(n=n, positive_pct=sum(c for v, c in hist.items() if v > 0) / n * 100,
                mean=sum(v * c for v, c in hist.items()) / n,
                median=(at((n - 1) // 2) + at(n // 2)) / 2, max=max(hist))


def build(source, check_full=False):
    config = json.loads((ROOT / 'config/scope.json').read_text())
    aliases = config['city_aliases']
    whitelist = set(config['part_a_city_whitelist'])
    files = {kind: source / f'yelp_dataset_vancouver-{kind}.json' for kind in ('business', 'review')}
    businesses, eligible = {}, {}
    for row in records(files['business']):
        key = row['business_id']
        if key in businesses:
            raise ValueError('Duplicate business ID')
        businesses[key] = row
        city = (row.get('city') or '').strip().lower()
        city = aliases.get(city, city.title())
        categories = {x.strip() for x in (row.get('categories') or '').split(',')}
        if row.get('state') == 'BC' and city.upper() in whitelist and 'Restaurants' in categories:
            eligible[key] = city
    counts, histograms = collections.Counter(), collections.defaultdict(collections.Counter)
    review_keys, yearly = {}, collections.defaultdict(collections.Counter)
    audit = collections.Counter(business_rows=len(businesses))
    for row in records(files['review']):
        key = row['review_id']
        if key in review_keys:
            raise ValueError('Duplicate review ID')
        review_keys[key] = tuple(row.get(k) for k in ('business_id', 'stars', 'date', 'useful', 'funny', 'cool', 'user_id'))
        audit['review_rows'] += 1
        year, stars = int(row['date'][:4]), integer(row['stars'])
        if stars not in range(1, 6):
            raise ValueError('Star rating outside 1-5')
        yearly[year][stars] += 1
        if row['business_id'] not in eligible:
            continue
        try:
            votes = {metric: integer(row[metric]) for metric in METRICS[:3]}
        except (KeyError, ValueError):
            audit['excluded_missing_votes'] += 1
            continue
        for metric in METRICS[:3]:
            if isinstance(row[metric], str):
                audit[metric + '_type_str'] += 1
        votes['total'] = sum(votes.values())
        group = year, eligible[row['business_id']], stars
        counts[group] += 1
        audit['included_reviews'] += 1
        for metric, value in votes.items():
            histograms[group, metric][value] += 1
    rows = []
    for group in sorted(counts):
        year, city, stars = group
        metrics = {}
        for metric in METRICS:
            hist = histograms[group, metric]
            metrics[metric] = dict(sum=sum(v*c for v, c in hist.items()),
                                   positive=sum(c for v, c in hist.items() if v > 0),
                                   hist=[list(x) for x in sorted(hist.items())])
        rows.append(dict(year=year, city=city, stars=stars, n=counts[group], metrics=metrics))
    hashes = {p.name: digest(p) for p in files.values()}
    if check_full:
        path = source / 'yelp_dataset_vancouver-review_full.json'
        seen = set()
        for row in records(path):
            key = row['review_id']
            if key in seen:
                raise ValueError('Duplicate full-text review ID')
            seen.add(key)
            fields = tuple(row.get(k) for k in ('business_id', 'stars', 'date', 'useful', 'funny', 'cool', 'user_id'))
            if key not in review_keys or fields != review_keys[key]:
                raise ValueError('Full-text analytical fields do not match review table')
        if seen != set(review_keys):
            raise ValueError('Full-text review coverage differs')
        audit['full_rows'] = len(seen)
        hashes[path.name] = digest(path)
    meta = dict(audit=dict(audit), restaurants=len(eligible), cities=sorted(set(eligible.values())),
                files=hashes, source_directory='Included source JSON in the multipart data archive',
                **config)
    summary = []
    for stars in range(1, 6):
        hist = collections.Counter()
        for group in counts:
            if group[2] == stars:
                hist.update(histograms[group, 'total'])
        if hist:
            summary.append(dict(stars=stars, **stats(hist)))
    return dict(meta=meta, rows=rows), summary, yearly


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--check-full', action='store_true', help='Also verify review_full coverage and analytical fields')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true', help='Verify shipped app and summaries without writing')
    mode.add_argument('--write', action='store_true', help='Replace shipped aggregates and audit after successful validation')
    args = parser.parse_args()
    payload, summary, yearly = build(args.source_dir, args.check_full)
    app = ROOT / 'app/index.html'
    html = app.read_text()
    start = html.index('window.YELP=') + len('window.YELP=')
    existing, end = json.JSONDecoder().raw_decode(html[start:])
    if args.check:
        if payload['rows'] != existing['rows']:
            raise ValueError('Rebuilt aggregates differ from the shipped app')
        if payload['meta']['restaurants'] != existing['meta']['restaurants']:
            raise ValueError('Restaurant population differs')
        for name, sha in payload['meta']['files'].items():
            if existing['meta']['files'].get(name) != sha:
                raise ValueError(f'Source hash differs: {name}')
        for key, count in payload['meta']['audit'].items():
            if existing['meta']['audit'].get(key, 0) != count:
                raise ValueError(f'Audit count differs: {key}')
        audit_file = json.loads((ROOT / 'app/docs/audit.json').read_text())
        if audit_file['meta'] != existing['meta']:
            raise ValueError('App metadata and audit.json differ')
        with (ROOT / 'app/docs/rating-summary.csv').open() as handle:
            shipped = list(csv.DictReader(handle))
        if len(shipped) != len(summary):
            raise ValueError('Summary row count differs')
        for actual, expected in zip(shipped, summary):
            for key, value in expected.items():
                if abs(float(actual[key]) - value) > 1e-10:
                    raise ValueError(f'Summary differs: stars {expected["stars"]}, {key}')
        print('PASS: all aggregate rows, source hashes, audit counts and summary values match.')
    else:
        # Serialize only after all input parsing and optional full-text checks succeeded.
        encoded = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
        app.write_text(html[:start] + encoded + html[start + end:])
        (ROOT / 'app/docs/audit.json').write_text(json.dumps(dict(meta=payload['meta'], summary=summary), indent=2) + '\n')
        with (ROOT / 'app/docs/rating-summary.csv').open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=('stars', 'n', 'positive_pct', 'mean', 'median', 'max'))
            writer.writeheader()
            writer.writerows(summary)
        print('Wrote aggregate app data, audit and rating summary. Raw data were not copied.')
    print(f'{len(payload["rows"])} groups; {payload["meta"]["audit"]["included_reviews"]:,} included reviews.')
    for year in (2008, 2020):
        c = yearly[year]
        print(f'{year}: 1 star {c[1]/sum(c.values()):.1%}, 5 stars {c[5]/sum(c.values()):.1%}')


if __name__ == '__main__':
    main()
