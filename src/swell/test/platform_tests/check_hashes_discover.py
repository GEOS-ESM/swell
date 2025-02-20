from swell.utilities.logger import get_logger
import swell.utilities.pinned_versions.check_hashes import check_hashes

logger = get_logger("CheckHashesTest")
bundle = "/discover/nobackup/projects/gmao/advda/jedi_bundles/current_pinned_jedi_bundle/source/"
check_hashes(bundle, logger)
