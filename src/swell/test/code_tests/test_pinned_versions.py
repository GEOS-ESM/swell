import os
import unittest
import subprocess
from swell.utilities.logger import Logger
from swell.test.code_tests.testing_utilities import suppress_stdout
from swell.utilities.pinned_versions.check_hashes import check_hashes


class PinnedVersionsTest(unittest.TestCase):

    def test_wrong_hash(self) -> None:
        logger = Logger("PinnedVersionsTest")
        jedi_bundle_dir = "jedi_bundle/"
        if not os.path.exists(jedi_bundle_dir):
            os.makedirs(jedi_bundle_dir)

        # Clone oops repository in jedi_bundle (develop hash)
        if not os.path.exists(jedi_bundle_dir + "oops"):
            cmd = ["git", "clone", "https://github.com/JCSDA/oops.git"]
        else:
            cmd = ["git", "checkout", "develop"]

        subprocess.run(cmd, cwd=jedi_bundle_dir, stderr=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL)
        abort_message = "Wrong commit hashes found for these repositories in jedi_bundle: [oops]"
        # Run check hash (expect abort)
        with self.assertRaises(SystemExit) as abort, suppress_stdout():
            check_hashes(jedi_bundle_dir, logger)
            self.assertEqual(abort.exception, abort_message)
