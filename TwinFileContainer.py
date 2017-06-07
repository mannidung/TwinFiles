import datetime
import hashlib
import os

BLOCKSIZE = 4096


class TwinFileContainer(object):

    def __init__(self, verbosity=0):
        self._filedict = {}
        self._map_is_filled = False
        self._is_purged = False
        self._verbosity = verbosity

    def scan_directory(self, path):
        for root, subdirs, files in os.walk(path):
            print()
            self._print_message('--\nscanning ' + root, verbosity=1)
            for subdir in subdirs:
                self._print_message('\t- subdirectories ' + subdir, verbosity=2)

            for filename in files:
                file_path = os.path.join(root, filename)
                self._print_message('\t- file %s (full path: %s)' % (filename, file_path), verbosity=2)
                self.hash_file(file_path)

        self._print_message(self._filedict, verbosity=2)
        self._map_is_filled = True

    def hash_file(self, absolute_path):
        hasher = hashlib.sha256()
        with open(absolute_path, 'rb') as this_file:
            buffer = this_file.read(BLOCKSIZE)
            while len(buffer) > 0:
                hasher.update(buffer)
                buffer = this_file.read(BLOCKSIZE)
        file_hash = hasher.hexdigest()
        self._print_message(file_hash, verbosity=2)
        if file_hash not in self._filedict.keys():
            self._filedict[file_hash] = [absolute_path]
        else:
            self._filedict[file_hash].append(absolute_path)

    def print_doubles(self):
        self._test_filled_and_purged()
        print("Doubles found:")
        for key in self._filedict.keys():

            for path in self._filedict[key]:
                print('\t' + path)
            print("\n")

    def print_doubles_to_file(self, path="default"):
        if path is "default":
            path = "./file_doubles_{0}.txt".format(datetime.datetime.now())
        self._test_filled_and_purged()
        with open(path, 'w') as this_file:
            for key in self._filedict.keys():
                for path in self._filedict[key]:
                    this_file.write(path + "\n")
                this_file.write("\n")

    def return_file_doubles_dict(self):
        return self._filedict.copy()

    def _print_message(self, message, verbosity=0):
        if verbosity <= self._verbosity:
            print(message)

    def _purge_nondoubles(self):
        nondouble_keys = []
        for key in self._filedict.keys():
            if len(self._filedict[key]) < 2:
                nondouble_keys.append(key)
        for key in nondouble_keys:
            del self._filedict[key]

    def _test_filled_and_purged(self):
        if not self._map_is_filled:
            raise AssertionError('No folder has been scanned')
        if not self._is_purged:
            self._purge_nondoubles()
            self._is_purged = True
