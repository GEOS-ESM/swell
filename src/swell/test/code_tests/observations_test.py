# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

import unittest
from unittest.mock import Mock

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
