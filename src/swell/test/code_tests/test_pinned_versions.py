import os
import unittest
import subprocess
import shutil
import atexit
from swell.utilities.logger import get_logger
from swell.utilities.exceptions import SwellError
from swell.test.code_tests.testing_utilities import suppress_stdout
from swell.utilities.pinned_versions.check_hashes import check_hashes
from swell.utilities.test_cache import get_test_cache


class PinnedVersionsTest(unittest.TestCase):

    def test_wrong_hash(self) -> None:
        logger = get_logger("PinnedVersionsTest")

        jedi_bundle_dir = "jedi_bundle/"
        test_cache = get_test_cache()

        if test_cache:
            jedi_bundle_dir = os.path.join(test_cache, jedi_bundle_dir)

        if not os.path.exists(jedi_bundle_dir):
            os.makedirs(jedi_bundle_dir)
            # Remove directory after the test
            atexit.register(lambda: shutil.rmtree(jedi_bundle_dir))

        # Clone oops repository in jedi_bundle (develop hash)
        if not os.path.exists(jedi_bundle_dir + "oops"):
            cmd = ["git", "clone", "https://github.com/JCSDA/oops.git"]
            wd = jedi_bundle_dir
        else:
            cmd = ["git", "switch", "develop"]
            wd = os.path.join(jedi_bundle_dir, 'oops')

        subprocess.run(cmd, cwd=wd, stderr=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL)
        abort_message = "Wrong commit hashes found for these repositories in jedi_bundle: [oops]"
        # Run check hash (expect abort)
        with self.assertRaises(SwellError) as abort, suppress_stdout():
            log_level = logger.level
            # Set logger priority to 60. This number sets the minimum level of message
            # that the logger can register (Where message criticality ascends from 0 to 50).
            # By setting a level of 60, we suppress all messages for the purpose of not polluting
            # the stream with confusing warnings, which are generated as part of the test process.
            logger.setLevel(60)
            check_hashes(jedi_bundle_dir, logger)
            self.assertEqual(abort.exception, abort_message)
            # Reset level of logger to its original value
            logger.setLevel(log_level)
