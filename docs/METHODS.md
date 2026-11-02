# Methods and data

## Source populations

The course-provided Yelp Vancouver JSON includes 17,292 businesses and 622,690 reviews; the user analysis describes 138,375 user IDs. Review coverage ends January 28, 2021. Business-profile and user-profile `review_count` fields are not interchangeable with counts in the supplied review table.

The extension selects businesses with an exact `Restaurants` category token, state BC, and a normalized city in the Part A whitelist, then joins reviews on `business_id`. Open and closed businesses remain included. This is a city-label approximation of Metro Vancouver, not a spatial boundary test. It yields 7,501 restaurant businesses and 426,719 reviews.

`app/docs/audit.json` records scope, city aliases, source-file hashes and audit counts; `rating-summary.csv` contains the default combined-vote results. All 837 aggregate groups match the raw-source calculations.

## Reaction measures

Negative = 1-2 stars; positive = 4-5; 3 stars remain a middle category.

- Combined votes = Useful + Funny + Cool.
- Share receiving a reaction = reviews with at least one selected vote / reviews in that group.
- Mean = selected votes / reviews.
- Median is computed from the combined vote-frequency distribution, including zeros, rather than averaging subgroup medians.

Vote strings were validated as nonnegative integers during data preparation. No included review needed exclusion for invalid votes. The full-text review table was checked against review IDs and analytical fields; it was not appended as another sample.

The app stores aggregates by review year, normalized city and star rating, including vote histograms. Filtering combines these aggregates and recomputes the charts and displayed interpretation.

## Findings and limits

The pooled combined-vote reaction rates are 58.6% for negative and 47.1% for positive reviews. Negative and positive groups contain 87,394 and 269,444 reviews respectively. Their means are 2.18 and 1.82 votes; medians are 1 and 0.

The direction reverses in the 2020 and partial-2021 review cohorts. A cohort is defined by review date, not vote date; cumulative votes may have arrived later. Useful, Funny and Cool are different signals, and the pooled pattern is not universal across them.

Exposure, readership, vote timing, review length, reviewer activity and restaurant mix are not controlled. Reactions do not measure customers, satisfaction prevalence or sales. Findings are descriptive; no treatment, prediction or measured operational benefit is claimed.

## Reproduction boundary

The app can reproduce its displayed calculations from the shipped aggregates. The AI-authored `scripts/build_data.py` rebuilds and checks these aggregates from authorized local raw JSON, using the explicit scope in `config/scope.json`. `scripts/audit_project.py` verifies headline metrics. Raw files are excluded; see [reproduction instructions](REPRODUCE.md). Tableau still requires the matching authorized raw files and a working installation.

Reference: [Yelp dataset documentation](https://www.yelp.com/dataset/documentation/main). The course-provided subset, rather than a fresh download of the latest Yelp dataset, is the actual source used here.
