# Reproduce the data

Python 3.10 or later, standard library only. Run from the repository root. Supply an authorized local copy of the **matching course subset**, not the latest Yelp download.

## Verify all shipped app results

```sh
python3 scripts/build_data.py --source-dir "/path/to/Yelp_Vancouver_json" --check --check-full
```

Required files: `yelp_dataset_vancouver-business.json`, `yelp_dataset_vancouver-review.json` and, for `--check-full`, `yelp_dataset_vancouver-review_full.json`. Files are newline-delimited JSON objects. The program validates business and review identifiers, checks source hashes, normalizes cities from `config/scope.json`, selects exact restaurant category tokens and rebuilds all year/city/star vote histograms. It compares counts, sums, reaction counts and summary statistics with the shipped app. The optional full-text check also verifies IDs, coverage and analytical fields; it does not append the full-text table as another sample.

## Rebuild the aggregate files

```sh
python3 scripts/build_data.py --source-dir "/path/to/Yelp_Vancouver_json" --write --check-full
```

This explicitly replaces the data embedded in `app/index.html`, `app/docs/audit.json` and `app/docs/rating-summary.csv` after validation. It preserves the app's presentation code. Raw records and input paths are not written to the repository. Without `--check-full`, the rebuilt metadata does not claim a full-text check.

## Verify the Tableau headline populations

```sh
python3 scripts/audit_project.py --source-dir "/path/to/Yelp_Vancouver_json"
```

Also requires `yelp_dataset_vancouver-user.json`. Prints the restaurant average and profile review total, annual review shares, and user-profile concentration. This verifies numerical definitions independently of Tableau's rendering; it cannot certify Tableau interactions.

## Run synthetic edge-case tests

```sh
python3 -m unittest discover -s tests -v
```

Tests cover zeros and outliers in an even-sized median, invalid votes, exact category matching, a city alias, duplicate review IDs and mismatched full-text fields. These are small synthetic fixtures, not additional empirical findings.
