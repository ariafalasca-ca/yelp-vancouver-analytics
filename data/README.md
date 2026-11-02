# Raw data is not included

Use an authorized copy of the course-provided Yelp Vancouver subset. A current Yelp Open Dataset download may not contain the same records or geographic coverage.

Place these files here, or use Tableau's source-relinking dialog to locate them:

- `yelp_dataset_vancouver-business.json`
- `yelp_dataset_vancouver-review.json`
- `yelp_dataset_vancouver-user.json`

Open the workbooks in `../tableau/`. Their connection directories point to `../data`; use the source-relinking dialog if Tableau cannot locate the files.

The web extension requires none of these files. Its aggregate data are embedded in `../app/index.html`.

Raw data, user profiles and review text must not be committed here. Yelp and course-source material remain subject to their original terms.
