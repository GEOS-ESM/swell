import os
import unittest
import subprocess
from datetime import datetime as dt
from swell.utilities.logger import Logger
from swell.utilities.get_channels import get_channels
from swell.utilities.observing_system_records import ObservingSystemRecords


def setup_geos_mksi(branch):
    url = "https://github.com/GEOS-ESM/GEOS_mksi.git"
    # Clone repo if not already cloned
    if not os.path.exists("GEOS_mksi"):
        git_clone_cmd = ["git", "clone", "-b", branch, url, "GEOS_mksi"]
        subprocess.run(git_clone_cmd, stderr=subprocess.DEVNULL)
    else:
        cwd = os.getcwd()
        os.chdir("GEOS_mksi")
        git_checkout_cmd = ['git', 'checkout', branch]
        subprocess.run(git_checkout_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(cwd)


class GenerateObservingSystemTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = Logger("GenerateObservingSystemTest")
        cls.observing_system_records_path = "./output/"
        cls.dt_cycle_time = dt.strptime("20211212T000000Z", "%Y%m%dT%H%M%SZ")
        cls.path_to_gsi_records = os.path.join("GEOS_mksi/", "sidb")

    def test_geos_mksi_main(self):

        """ Testing abort for if on main branch for GEOS_mksi  """

        # Clone Geos_mksi (main branch) and parse yamls
        observations = ["cris-fsr_npp"]
        setup_geos_mksi("main")
        sat_records = ObservingSystemRecords("channel")
        sat_records.parse_records(self.path_to_gsi_records)
        sat_records.save_yamls(self.observing_system_records_path, observations)

        # Check that get_channels aborts for  cris-fsr_npp
        abort_message = "\nHERE IS THE TRACEBACK: \n----------------------\n\n" + \
                        "Missing active channels for cris-fsr_npp, " + \
                        "Confirm that you are using the right version of GEOSmksi"
        with self.assertRaises(SystemExit) as abort:
            get_channels(self.observing_system_records_path, observations[0],
                         self.dt_cycle_time, self.logger)
            self.assertEqual(abort.exception, abort_message)

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
