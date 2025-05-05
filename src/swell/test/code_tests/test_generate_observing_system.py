import os
import unittest
import subprocess
import shutil
import atexit
from datetime import datetime as dt
from swell.utilities.logger import get_logger
from swell.utilities.exceptions import SwellError
from swell.utilities.get_channels import get_channels
from swell.test.code_tests.testing_utilities import suppress_stdout
from swell.utilities.observing_system_records import ObservingSystemRecords
from swell.utilities.test_cache import get_test_cache


def setup_geos_mksi(reference: str):
    """
    Clone GEOS-mksi and checkout a branch or commit specified by `reference`.
    """

    geos_mksi_path = 'GEOS_mksi'

    test_cache = get_test_cache()
    if test_cache:
        geos_mksi_path = os.path.join(test_cache, geos_mksi_path)

    url = "https://github.com/GEOS-ESM/GEOS_mksi.git"
    # Clone repo if not already cloned
    if not os.path.exists(geos_mksi_path):
        git_clone_cmd = ["git", "clone", url, geos_mksi_path]
        subprocess.run(git_clone_cmd, stderr=subprocess.DEVNULL)
        # Delete the GEOS_mksi directory after the test runs, to keep things clean
        atexit.register(lambda: shutil.rmtree("GEOS_mksi"))

    git_checkout_cmd = ["git", "checkout", reference]
    subprocess.run(git_checkout_cmd, cwd=geos_mksi_path, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


class GenerateObservingSystemTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = get_logger("GenerateObservingSystemTest")
        observing_system_records_path = "output/"
        test_cache = get_test_cache()
        if test_cache:
            observing_system_records_path = os.path.join(test_cache, observing_system_records_path)
        else:
            observing_system_records_path = os.path.join('./', observing_system_records_path)
        cls.observing_system_records_path = observing_system_records_path
        cls.dt_cycle_time = dt.strptime("20211212T000000Z", "%Y%m%dT%H%M%SZ")
        geos_mksi_path = 'GEOS_mksi/'
        if test_cache:
            geos_mksi_path = os.path.join(test_cache, geos_mksi_path)
        cls.path_to_gsi_records = os.path.join(geos_mksi_path, "sidb")

    def test_geos_mksi_broken(self):

        """ Testing abort if on a known bad commit of GEOS_mksi  """
        bad_reference = "bb332daf362891260f87bfa73075615461848325"

        # Clone Geos_mksi (main branch) and parse yamls
        observations = ["cris-fsr_npp"]
        setup_geos_mksi(bad_reference)
        sat_records = ObservingSystemRecords("channel")
        sat_records.parse_records(self.path_to_gsi_records)
        sat_records.save_yamls(self.observing_system_records_path, observations)

        # Check that get_channels aborts for  cris-fsr_npp
        abort_message = "\nHERE IS THE TRACEBACK: \n----------------------\n\n" + \
                        "Missing active channels for cris-fsr_npp, " + \
                        "Confirm that you are using the right version of GEOSmksi"

        with self.assertRaises(SwellError) as abort, suppress_stdout():
            log_level = self.logger.level
            # Set logger priority to 60. This number sets the minimum level of message
            # that the logger can register (Where message criticality ascends from 0 to 50).
            # By setting a level of 60, we suppress all messages for the purpose of not polluting
            # the stream with confusing warnings, which are generated as part of the test process.
            self.logger.setLevel(60)
            get_channels(self.observing_system_records_path, observations[0],
                         self.dt_cycle_time, self.logger)
            self.assertEqual(abort.exception, abort_message)
            # Reset level of logger to its original value
            self.logger.setLevel(log_level)

    def test_geos_mksi_develop(self):

        """ Test to show that GEOS_mksi's develop branch works as expected  """

        # Clone Geos_mksi (develop branch) and parse yamls
        observations = ["cris-fsr_npp"]
        setup_geos_mksi("develop")
        sat_records = ObservingSystemRecords("channel")
        sat_records.parse_records(self.path_to_gsi_records)
        sat_records.save_yamls(self.observing_system_records_path, observations)
        _, active_chs = get_channels(self.observing_system_records_path, observations[0],
                                     self.dt_cycle_time, self.logger)
        assert active_chs is not None

    def test_expected_active_channels(self):

        """ Test for expected active channels for some observation types"""

        # Prepare expected use flags
        avhrr3_n18_use_flags = [-1, 1, 1]
        mhs_metop_c_use_flags = [1, 1, 1, 1, 1]
        gmi_gpm_use_flags = [-1, -1, -1, -1, 1, 1, 1, -1, -1, 1, -1, 1, 1]
        amsua_n19_use_flags = [-1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, 1, 1, -1]
        use_flags = [amsua_n19_use_flags, avhrr3_n18_use_flags,
                     gmi_gpm_use_flags, mhs_metop_c_use_flags]
        observations = ["amsua_n19", "avhrr3_n18", "gmi_gpm", "mhs_metop-c"]

        # Clone Geos_mksi (develop branch) and parse yamls
        setup_geos_mksi("develop")
        sat_records = ObservingSystemRecords("channel")
        sat_records.parse_records(self.path_to_gsi_records)
        sat_records.save_yamls(self.observing_system_records_path, observations)

        for idx in range(len(observations)):
            _, generated_use_flags = get_channels(self.observing_system_records_path,
                                                  observations[idx], self.dt_cycle_time,
                                                  self.logger)
            assert (use_flags[idx] == generated_use_flags)
