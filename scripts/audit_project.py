#!/usr/bin/env python3
"""Recompute portfolio headline metrics from authorized local course JSON."""
import argparse
import json
from pathlib import Path
from build_data import build, records, integer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    args = parser.parse_args()
    payload, summary, yearly = build(args.source_dir)
    meta = payload['meta']
    aliases = meta['city_aliases']
    whitelist = set(meta['part_a_city_whitelist'])
    eligible = []
    for row in records(args.source_dir / 'yelp_dataset_vancouver-business.json'):
        city = (row.get('city') or '').strip().lower()
        city = aliases.get(city, city.title())
        if row.get('state') == 'BC' and city.upper() in whitelist and 'Restaurants' in {x.strip() for x in (row.get('categories') or '').split(',')}:
            eligible.append(row)
    users, counts, high, high_counts = set(), 0, 0, 0
    for row in records(args.source_dir / 'yelp_dataset_vancouver-user.json'):
        if row['user_id'] in users:
            raise ValueError('Duplicate user ID')
        users.add(row['user_id'])
        n = integer(row['review_count'])
        counts += n
        if n > 100:
            high += 1
            high_counts += n
    result = dict(restaurants=len(eligible), restaurant_mean_rating=sum(float(r['stars']) for r in eligible)/len(eligible),
                  restaurant_profile_review_counts=sum(integer(r['review_count']) for r in eligible),
                  users=len(users), users_over100_pct=100*high/len(users),
                  share_profile_review_counts_pct=100*high_counts/counts,
                  review_rows=meta['audit']['review_rows'], included_restaurant_reviews=meta['audit']['included_reviews'],
                  annual_shares={str(y): {str(star): 100*yearly[y][star]/sum(yearly[y].values()) for star in (1, 5)} for y in (2008, 2020)})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
