"""
"""
import os
import copy
import time
import fnmatch

DELETION = 'd'
ADDITION = 'a'
MODIFICATION = 'm'


class PathDescriptor(object):

    def __init__(self, path):
        self.path = path

    def key(self):
        return self.path


class BaseWatcher(object):

    def __init__(self, directories, ignore, mask='*'):
        self.paths = []
        self.responders = []
        for directory in directories:
            self.register_path(directory)
        self.ignore = ignore
        self.mask = mask

    def file_matches_mask(self, file):
        return fnmatch.fnmatch(file, self.mask)

    def register_path(self, path):
        self.paths.append(PathDescriptor(path))

    def register_responder(self, responder):
        self.responders.append(responder)

    def get_changes(self):
        pass

    def watch(self):
        while True:
            changes = self.get_changes()
            if changes:
                for responder in self.responders:
                    responder.respond(changes)


class ModTimeWatcher(BaseWatcher):

    def __init__(self, directories, ignore, mask='*'):
        self.path_info = self.previous_path_info = {}
        super(ModTimeWatcher, self).__init__(directories, ignore, mask)

    def register_path(self, path):
        super(ModTimeWatcher, self).register_path(path)
        self.crawl_path(self.paths[-1])

    def crawl_path(self, path_descriptor):
        info = self.path_info[path_descriptor.key()] = {}
        for path, dirs, files in os.walk(path_descriptor.path):
            for file in [os.path.abspath(os.path.join(path, filename)) for filename in files]:
                try:
                    info[file] = os.path.getmtime(file)
                except OSError:
                    #file was removed as we were trying to access it, don't include it
                    pass

    def crawl_paths(self):
        for p in self.paths:
            self.crawl_path(p)

    def get_changes(self, sleep_interval=0.5):
        time.sleep(sleep_interval)
        self.previous_path_info = copy.deepcopy(self.path_info)
        self.crawl_paths()
        changes = []
        a = self.path_info
        b = self.previous_path_info
        keys = set(a.keys() + b.keys())
        for key in keys:
            files = set(a[key].keys() + b[key].keys())
            for file in files:
                change_type = None
                delta = 0
                if file not in a[key]:
                    change_type = DELETION
                elif file not in b[key]:
                    change_type = ADDITION
                else:
                    if a[key][file] != b[key][file]:
                        delta = a[key][file] - b[key][file]
                        change_type = MODIFICATION

                if change_type and self.file_matches_mask(file):
                    changes.append((change_type, file, delta))

        return changes

Watcher = ModTimeWatcher
