from swell.utilities.logger import Logger
import swell.utilities.pinned_versions.check_hashes import check_hashes

logger = Logger("CheckHashesTest")
bundle = "/discover/nobackup/projects/gmao/advda/jedi_bundles/current_pinned_jedi_bundle/source/"
check_hashes(bundle, logger)
