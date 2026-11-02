# Tableau workbooks

## Open the dashboards

1. Download and extract the repository.
2. Run `python3 scripts/extract_data.py` to unpack the included source data into `data/`.
3. Open a `.twb` file from `tableau/` in Tableau Desktop.
4. If prompted for a source, locate the matching extracted JSON. See [data setup](../data/README.md).

The workbooks contain dashboard definitions, not embedded data. The web extension runs separately from `app/index.html` and needs no raw files.

## Beyond the Stars

The eligible population is restaurants in the documented Metro Vancouver city-label scope. With all cuisines selected, the source calculations give:

| Metric | Value | Definition |
|---|---:|---|
| Restaurants | 7,501 | Distinct eligible business IDs |
| Average rating | 3.45 | Unweighted mean of eligible business-profile star ratings; displayed as 3.5 |
| Profile review counts | 412,748 | Sum of eligible business-profile `review_count` |

Cuisine categories assign one class using ordered conditions, even when a restaurant has multiple cuisines. The Top 10 ranks business IDs by profile review count. The star-distribution chart follows the current map viewport, so its geographic scope differs from the overall KPIs and Top 10.

## Yelp Reviews

- Annual distributions use the supplied review table and compare 2008-2020, excluding the incomplete 2021 year.
- Monthly activity compares 2019-2020. The average-rating chart uses an explicitly labeled restricted 3-4-star scale.
- The user dashboard groups users by profile review count. Both percentage panels use a 0-100% scale. Their denominators are users and summed profile review counts respectively, not the local restaurant-review sample.

The dashboards describe observed patterns. Review-count rankings are not rankings of quality, and changes around COVID-19 are not causal estimates.
