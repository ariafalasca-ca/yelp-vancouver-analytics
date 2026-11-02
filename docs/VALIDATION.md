# Data checks

## Source consistency

- All **837 year/city/star aggregate groups**, representing **426,719 restaurant reviews**, match calculations from the business and review JSON: review counts, vote totals, numbers receiving a vote and complete vote-frequency distributions.
- Recorded SHA-256 source hashes match the input files.
- The review and full-text tables each contain 622,690 unique review IDs with matching analytical fields. The full-text table is a consistency check, not an additional sample.
- Headline populations reproduce: 7,501 restaurants; 412,748 summed business-profile review counts; mean restaurant rating 3.4521397; 138,375 unique users.
- Users with over 100 profile reviews represent 8.77037% of users and 71.81241% of summed profile review counts.
- Annual one/five-star shares reproduce: 2008 2.0%/26.7%; 2020 16.3%/42.4%.

## Reproduction tools

The data builder passed a rebuild-and-check round trip. Five synthetic tests cover exact category selection and city aliases, medians including zeros and outliers, invalid votes, duplicate review IDs and inconsistent full-text fields.

## App behavior

Targeted browser checks cover default results, vote-type selection, the 2020 cohort comparison, a single-star selection and a location/year combination without data. The empty selection displays no reviews rather than inventing a comparison.

These checks support the numerical results and the tested interactions; they do not establish causal effects, representative sampling or measured business outcomes.

See [reproduction instructions](REPRODUCE.md) for commands and required local source files.
