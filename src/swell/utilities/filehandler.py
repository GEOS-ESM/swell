import os
import glob
import datetime as dt
from shutil import copyfile

def get_data(config):

    if not config or config is None: return 0
    if not isinstance(config, list): raise SWELLConfigError(config)

    if 'copy_files' in config[0]: return StageFileHandler(config)
    if 'link_files' in config[0]: return GetDataFileHandler(config)

    return GetDataFileHandler(config)

#----------------------------------------------------------------------------

class FileHandler(object):

    def __init__(self, config):

        self.config = copy.deepcopy(config)
        self.listing = []
#----------------------------------------------------------------------------

    def is_ready(self, fc):

        if fc.num_files() < fc.min_count: return False

        for srcfile, dstfile in fc:

            if not os.path.isfile(srcfile): continue

            mt   = dt.datetime.fromtimestamp(os.stat(srcfile).st_mtime)
            now  = dt.datetime.now()
            age  = (now - mt).total_seconds()

            if age > fc.min_age: return False

        return True

#----------------------------------------------------------------------------

    def copy(self, src, dst):
        """File handler - copies a file

           Parameters
           ----------
           src : string, required
             Source file to be copied.

           dst : string, required
             Destination file to be created.
        """

        if not os.path.isfile(src):
            raise SWELLFileError('Source file does not exist: "' + src + '"')

        try:
            copyfile(src, dst)
        except Exception as e:
            raise SWELLFileError(str(e))

#----------------------------------------------------------------------------

    def link(self, src, dst):
        """File handler - Symbolically links a file

           Parameters
           ----------
           src : string, required
             Source file to be linked.

           dst : string, required
             Destination link file to be created.
        """

        if not os.path.isfile(src):
            raise SWELLFileError('Source file does not exist: "' + src + '"')

        try:
            if os.path.islink(dst):
                os.remove(dst)
            if os.path.isfile(dst):
                raise SWELLFileError('File exists where link expected: "' + dst + '"')
            if not os.path.isfile(dst):
                os.symlink(src, dst)
        except Exception as e:
            raise SWELLFileError(str(e))

#----------------------------------------------------------------------------

class StageFileHandler(FileHandler):

    def list(self, strict=False):

        listing = []
        for group in self.config:

            for directive, listing in iter(group.items()):

                link = False
                if directive == 'link_files': link = True
                fc = FileCollection({'link': link})

                for record in listing:

                    src = record[0]
                    dst = record[1]

                    filelist = glob.glob(src)

                    if not filelist and strict:
                        raise SWELLConfigError('Source inputs not found "'
                                               + src + '"')

                    for srcfile in filelist:
                        bname = os.path.basename(srcfile)
                        dstfile = os.path.join(dst, bname)
                        fc.update(srcfile, dstfile)

                listing.append(fc)

        return listing

#----------------------------------------------------------------------------

class GetDataFileHandler(FileHandler):

    def list(self):

        for collection in self.config:

            # Get collection parameters

            options = {k:v for k,v in iter(collection.items())
                       if k not in ['src','dst','files']}

            src  = str(collection.get('src', ''))
            dst  = str(collection.get('dst', ''))

            # Create file listing

            fc = FileCollection(options)
            for file in collection.get('files', ['*']):

                record = file.split() + ['']

                srcfile = os.path.join(src,record[0])
                dstfile = os.path.join(dst,record[1])
                if os.path.isabs(record[0]): srcfile = record[0]
                if record[1] and os.path.isabs(record[1]): dstfile = record[1]

                filelist = glob.glob(srcfile)

                for srcfile in filelist:
                    fc.update(srcfile, dstfile)

            listing.append(fc)

        return listing

#----------------------------------------------------------------------------

class FileCollection(object):

    def __init__(self, config):

        self.config = copy.deepcopy(config)

        self.listing   = []
        self.link      = config.get('link', False)
        self.min_count = config.get('min_count', 1)
        self.min_age   = config.get('min_age', 0)

#----------------------------------------------------------------------------

    def update(self, srcfile, dstfile):

        self.listing.append((srcfile, dstfile))

#----------------------------------------------------------------------------

    def num_files(self): return len(self.listing)

#----------------------------------------------------------------------------

    def __iter__(self): for v in self.listing: yield v
