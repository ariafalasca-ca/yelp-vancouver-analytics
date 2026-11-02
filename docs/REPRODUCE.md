# Reproduce the data

Python 3.10 or later, standard library only. Run from the repository root. Run `python3 scripts/extract_data.py` to verify and extract the included archive parts into `data/`. Use `--source-dir data` in the commands below. This is the matching historical course subset, not the latest Yelp download.

## Verify all shipped app results

```sh
python3 scripts/build_data.py --source-dir data --check
```

The archive contains all files required for the app and headline checks. Required files: `yelp_dataset_vancouver-business.json`, `yelp_dataset_vancouver-review.json` and, for `--check-full`, `yelp_dataset_vancouver-review_full.json`. The optional `review_full` file is not included: it duplicates the review IDs and analytical fields and is not required by the app or workbooks. Files are newline-delimited JSON objects. The program validates business and review identifiers, checks source hashes, normalizes cities from `config/scope.json`, selects exact restaurant category tokens and rebuilds all year/city/star vote histograms. It compares counts, sums, reaction counts and summary statistics with the shipped app. The optional full-text check also verifies IDs, coverage and analytical fields; it does not append the full-text table as another sample.

## Rebuild the aggregate files

```sh
python3 scripts/build_data.py --source-dir data --write
```

This explicitly replaces the data embedded in `app/index.html`, `app/docs/audit.json` and `app/docs/rating-summary.csv` after validation. It preserves the app's presentation code. Raw records and input paths are not written to the repository. Without `--check-full`, the rebuilt metadata does not claim a full-text check.

## Verify the Tableau headline populations

```sh
python3 scripts/audit_project.py --source-dir data
```

Also requires `yelp_dataset_vancouver-user.json`. Prints the restaurant average and profile review total, annual review shares, and user-profile concentration. This verifies numerical definitions independently of Tableau's rendering; it cannot certify Tableau interactions.

## Run synthetic edge-case tests

```sh
python3 -m unittest discover -s tests -v
```

Tests cover zeros and outliers in an even-sized median, invalid votes, exact category matching, a city alias, duplicate review IDs and mismatched full-text fields. These are small synthetic fixtures, not additional empirical findings.
