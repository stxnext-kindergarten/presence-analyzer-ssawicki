# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import os.path
import json
import datetime
import unittest

from presence_analyzer import main, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {'user_id': 10, 'name': 'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test mean time weekday view.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/0')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data),
            [
                ['Mon', 0],
                ['Tue', 30047.0],
                ['Wed', 24465.0],
                ['Thu', 23705.0],
                ['Fri', 0],
                ['Sat', 0],
                ['Sun', 0]
            ]
        )

    def test_presence_weekday_view(self):
        """
        Test presence weekday view.
        """
        resp = self.client.get('/api/v1/presence_weekday/0')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data),
            [
                ['Weekday', 'Presence (s)'],
                ['Mon', 0],
                ['Tue', 30047],
                ['Wed', 24465],
                ['Thu', 23705],
                ['Fri', 0],
                ['Sat', 0],
                ['Sun', 0]
            ]
        )

    def test_user_available_average_view(self):
        """
        Test presence weekday view.
        """
        resp = self.client.get('/api/v1/user_available_average/0')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/user_available_average/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data),
            [
                ['Mon', 0, 0],
                ['Tue', 34745000.0, 64792000.0],
                ['Wed', 33592000.0, 58057000.0],
                ['Thu', 38926000.0, 62631000.0],
                ['Fri', 0, 0],
                ['Sat', 0, 0],
                ['Sun', 0, 0]
            ]
        )


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_by_weekday(self):
        """
        Test groups presence entries by weekday.
        """
        self.assertEqual(
            utils.group_by_weekday(utils.get_data()[10]),
            [[], [30047], [24465], [23705], [], [], []]
        )

    def test_seconds_since_midnight(self):
        """
        Test calculates amount of seconds since midnight.
        """
        self.assertEqual(
            utils.seconds_since_midnight(
                datetime.datetime(
                    year=2014,
                    month=1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=1
                )
            ),
            1
        )
        self.assertEqual(
            utils.seconds_since_midnight(
                datetime.datetime(
                    year=2014,
                    month=1,
                    day=1,
                    hour=15,
                    minute=57,
                    second=44
                )
            ),
            57464
        )

    def test_interval(self):
        """
        Test calculates inverval in seconds between two datetime.time objects.
        """
        self.assertEqual(
            utils.interval(
                datetime.datetime(
                    year=2014,
                    month=1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=1
                ),
                datetime.datetime(
                    year=2014,
                    month=1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=2
                )
            ),
            1
        )

    def test_mean(self):
        """
        Test calculates arithmetic mean.
        """
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([1, 2]), 1.5)
        self.assertEqual(utils.mean([1.5, 2.8]), 2.15)

    def test_start_end_date_by_weekday(self):
        """
        Test groups start/end dates by weekday.
        """
        self.assertEqual(
            utils.start_end_date_by_weekday(utils.get_data()[10]),
            {
                'start': [[], [34745], [33592], [38926], [], [], []],
                'end': [[], [64792], [58057], [62631], [], [], []]
            }
        )


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
