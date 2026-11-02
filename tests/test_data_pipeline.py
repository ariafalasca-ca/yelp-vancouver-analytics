import collections
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('build_data', Path(__file__).resolve().parents[1] / 'scripts/build_data.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class DataPipelineTests(unittest.TestCase):
    def test_even_median_includes_zero_and_outlier(self):
        s = m.stats(collections.Counter({0: 2, 1: 1, 99: 1}))
        self.assertEqual(s['median'], 0.5)
        self.assertEqual(s['positive_pct'], 50)
        self.assertEqual(s['mean'], 25)

    def test_rejects_invalid_votes(self):
        for value in [True, None, '-1', '1.5', 'nan', '']:
            with self.assertRaises(ValueError):
                m.integer(value)

    def fixture(self, directory, duplicate=False, full_mismatch=False):
        businesses = [dict(business_id='r', city='Vancover', state='BC', categories='Food, Restaurants'),
                      dict(business_id='other', city='Vancouver', state='BC', categories='Restaurants Supplies')]
        reviews = [dict(review_id='a', business_id='r', stars=1, date='2020-01-01', useful='0', funny='0', cool='0'),
                   dict(review_id='b', business_id='r', stars=1, date='2020-02-01', useful='1', funny='2', cool='0'),
                   dict(review_id='c', business_id='other', stars=5, date='2020-03-01', useful='1', funny='0', cool='0')]
        full = [dict(r) for r in reviews]
        if full_mismatch:
            full[0]['useful'] = '9'
        if duplicate:
            reviews.append(reviews[0])
        for kind, rows in [('business', businesses), ('review', reviews), ('review_full', full)]:
            (directory / f'yelp_dataset_vancouver-{kind}.json').write_text(''.join(json.dumps(r)+'\n' for r in rows))

    def test_exact_category_alias_join_and_histogram(self):
        with tempfile.TemporaryDirectory() as d:
            self.fixture(Path(d))
            payload, summary, yearly = m.build(Path(d), True)
            self.assertEqual(payload['meta']['restaurants'], 1)
            self.assertEqual(payload['meta']['audit']['included_reviews'], 2)
            self.assertEqual(payload['rows'][0]['city'], 'Vancouver')
            self.assertEqual(payload['rows'][0]['metrics']['total']['hist'], [[0, 1], [3, 1]])
            self.assertEqual(summary[0]['median'], 1.5)
            self.assertEqual(sum(yearly[2020].values()), 3)

    def test_duplicate_reviews_fail(self):
        with tempfile.TemporaryDirectory() as d:
            self.fixture(Path(d), duplicate=True)
            with self.assertRaisesRegex(ValueError, 'Duplicate review'):
                m.build(Path(d))

    def test_full_text_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.fixture(Path(d), full_mismatch=True)
            with self.assertRaisesRegex(ValueError, 'analytical fields'):
                m.build(Path(d), True)


if __name__ == '__main__':
    unittest.main()
