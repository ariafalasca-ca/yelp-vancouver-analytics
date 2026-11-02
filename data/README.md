# Yelp Vancouver source data

The business, review and user JSON files used in this project are included as a **four-part ZIP archive**. The course instructor authorized sharing these course-provided files. Yelp and other source materials remain subject to their original terms; this repository does not grant a separate licence to the dataset.

## Extract the data

Download the **full repository** using Code → Download ZIP, then extract that download. From the repository root, run:

```sh
python3 scripts/extract_data.py
```

The command verifies all archive parts, reconstructs the ZIP and extracts these files into `data/`:

- `yelp_dataset_vancouver-business.json`
- `yelp_dataset_vancouver-review.json`
- `yelp_dataset_vancouver-user.json`

Then open a workbook in `tableau/`. If Tableau asks for a source, select the matching extracted JSON. The web app works without extraction.

## Archive parts

All four parts are required and are included when the full repository is downloaded:

- [Part 1](yelp-vancouver-data.zip.part01)
- [Part 2](yelp-vancouver-data.zip.part02)
- [Part 3](yelp-vancouver-data.zip.part03)
- [Part 4](yelp-vancouver-data.zip.part04)

The source files occupy approximately 372 MB uncompressed, or 169 MB in the archive. Parts stay below GitHub's per-file upload limit. [manifest.json](manifest.json) records sizes and SHA-256 checksums; extraction verifies each part and preserves the original JSON byte-for-byte. Extracted files remain ignored by Git to avoid duplicate copies.

The additional full-text review table duplicates the review IDs and analytical fields and is not required by either workbook. Tip and check-in tables are outside this project's scope. These extra tables are not included.
