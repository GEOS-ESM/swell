# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

import datetime
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

from swell.tasks.download_obs import DownloadObs
from swell.utilities.observations import get_provider_for_observation


class ObservationProviderTest(unittest.TestCase):

    def setUp(self):
        self.logger = Mock()
        self.ioda_names = [
            {'ioda name': 'aircraft', 'provider': 'ncdiag'},
            {'ioda name': 'abi_g18'},
        ]

    def test_provider_override_takes_precedence(self):
        provider = get_provider_for_observation(
            'aircraft', self.ioda_names, self.logger,
            provider_overrides={'aircraft': 'alternate_provider'},
        )

        self.assertEqual(provider, 'alternate_provider')
        self.logger.abort.assert_not_called()

    def test_metadata_provider_is_used_without_override(self):
        provider = get_provider_for_observation(
            'aircraft', self.ioda_names, self.logger,
            provider_overrides={},
        )

        self.assertEqual(provider, 'ncdiag')
        self.logger.abort.assert_not_called()

    def test_override_can_supply_missing_metadata_provider(self):
        provider = get_provider_for_observation(
            'abi_g18', self.ioda_names, self.logger,
            provider_overrides={'abi_g18': 'alternate_provider'},
        )

        self.assertEqual(provider, 'alternate_provider')
        self.logger.abort.assert_not_called()

    def test_invalid_override_mapping_aborts(self):
        self.logger.abort.side_effect = RuntimeError

        with self.assertRaises(RuntimeError):
            get_provider_for_observation(
                'aircraft', self.ioda_names, self.logger,
                provider_overrides=['ncdiag'],
            )

        self.logger.abort.assert_called_once()

    def test_empty_provider_override_aborts(self):
        self.logger.abort.side_effect = RuntimeError

        with self.assertRaises(RuntimeError):
            get_provider_for_observation(
                'aircraft', self.ioda_names, self.logger,
                provider_overrides={'aircraft': ''},
            )

        self.logger.abort.assert_called_once()


class IndexedDownloadTest(unittest.TestCase):

    def setUp(self):
        self.download_obs = DownloadObs.__new__(DownloadObs)
        self.download_obs.logger = Mock()
        self.window_begin = datetime.datetime(2025, 1, 1, 0, 0)
        self.window_end = datetime.datetime(2025, 1, 2, 0, 0)

    def _json_response(self, payload):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = payload
        return response

    def test_ogc_features_index_preserves_existing_url_handling(self):
        config = {
            'index_url': 'https://index.example/items',
            'index_params': {'content_category': 'OzoneSonde'},
            'index_url_property': 'url',
            'index_filename_parts': 2,
        }
        first_page = {
            'features': [{'properties': {'url': 'https://files.example/site/a.csv'}}],
            'links': [{'rel': 'next', 'href': 'https://index.example/items?offset=1'}],
        }
        second_page = {
            'features': [{'properties': {'url': 'https://files.example/site/b.csv'}}],
            'links': [],
        }

        with tempfile.TemporaryDirectory() as cycle_dir, \
             patch.object(self.download_obs, 'cycle_dir', return_value=cycle_dir), \
             patch('swell.tasks.download_obs.requests.Session') as session_factory, \
             patch.object(self.download_obs, '_download_file') as download_file:
            session = session_factory.return_value
            session.get.side_effect = [
                self._json_response(first_page), self._json_response(second_page),
            ]
            downloaded, failed = self.download_obs._download_obs_https_index(
                config, 'ozonesonde', self.window_begin, self.window_end, False)

        self.assertEqual((downloaded, failed), (2, 0))
        self.assertEqual(
            [call.args[1] for call in download_file.call_args_list],
            ['https://files.example/site/a.csv', 'https://files.example/site/b.csv'],
        )
        self.assertEqual(
            [call.args[2].rsplit('/', 1)[-1] for call in download_file.call_args_list],
            ['site_a.csv', 'site_b.csv'],
        )
        first_params = session.get.call_args_list[0].kwargs['params']
        self.assertEqual(first_params['content_category'], 'OzoneSonde')
        self.assertIn('datetime', first_params)
        self.assertEqual(session.get.call_args_list[1].kwargs['params'], None)

    def _run(self, config, pages):
        """Run the indexed download with mocked HTTP; return (result, session, download_file)."""
        with tempfile.TemporaryDirectory() as cycle_dir, \
             patch.object(self.download_obs, 'cycle_dir', return_value=cycle_dir), \
             patch('swell.tasks.download_obs.requests.Session') as session_factory, \
             patch('swell.tasks.download_obs.time.sleep'), \
             patch.object(self.download_obs, '_download_file') as download_file:
            session = session_factory.return_value
            session.get.side_effect = pages
            result = self.download_obs._download_obs_https_index(
                config, 'ozonesonde', self.window_begin, self.window_end, False)
        return result, session, download_file

    def _feature(self, url):
        return {'properties': {'url': url}}

    def test_empty_page_stops_even_with_next_link(self):
        first = {'features': [self._feature('https://files.example/a.csv')],
                 'links': [{'rel': 'next', 'href': 'https://index.example/items?offset=1'}]}
        empty = {'features': [],
                 'links': [{'rel': 'next', 'href': 'https://index.example/items?offset=2'}]}
        result, session, _ = self._run(
            {'index_url': 'https://index.example/items'},
            [self._json_response(first), self._json_response(empty)])
        self.assertEqual(result, (1, 0))
        self.assertEqual(session.get.call_count, 2)

    def test_empty_index_is_not_an_error(self):
        result, _, download_file = self._run(
            {'index_url': 'https://index.example/items'},
            [self._json_response({'features': [], 'links': []})])
        self.assertEqual(result, (0, 0))
        download_file.assert_not_called()
        self.download_obs.logger.abort.assert_not_called()

    def test_failed_query_is_retried_then_aborts(self):
        self.download_obs.logger.abort.side_effect = RuntimeError
        error = requests.ConnectionError('down')
        with self.assertRaises(RuntimeError):
            self._run({'index_url': 'https://index.example/items', 'index_retries': 2},
                      [error, error])
        self.download_obs.logger.abort.assert_called_once()
        retry_logs = [c.args[0] for c in self.download_obs.logger.info.call_args_list
                      if 'attempt 1 failed' in c.args[0]]
        self.assertEqual(len(retry_logs), 1)
