"""
Mutter

Plays sounds and renders notifications based on the result of a command run
when files are modified.

Can dynamically load Watchers, Responders and Notifiers.

Watchers generate events from the filesystem, Responders choose whether or not
to run the user's command. Notifiers display information to the user.

Simple text and audio notifiers provided.
Stupid os-agnostic watcher is included (uses a loop and file mod times).
Simple responder that requires a threshold in modification times to prevent
multiple runs if several files change in a short amount of time.

Example invokation:

mutter -c ./run_tests.sh -m "*.py"

See --help for usage.
"""

__author__ = "Travis Cline (travis.cline@gmail.com)"
__version__ = "0.0.1"

import sys
from optparse import OptionParser

from mutter.watchers import ModTimeWatcher
from mutter.notifiers import SoundNotifier
from mutter.responders import DeltaThresholdResponder


class Mutter(object):

    def __init__(self, options):

        # create watcher
        try:
            self.watcher = dynload(options.watcher)(options.directories, options.ignore, options.mask)
        except Exception, e:
            print 'Failed to load watcher: %s' % e
            sys.exit(1)

        # create notifier
        try:
            self.notifier = dynload(options.notifier)()
        except Exception, e:
            print 'Failed to load notifier: %s' % e
            sys.exit(1)

        # create responder
        try:
            self.responder = dynload(options.responder)(self.notifier, options.command)
        except Exception, e:
            print 'Failed to load responder: %s' % e
            sys.exit(1)

        # register responder
        self.watcher.register_responder(self.responder)

    def run(self):
        "main loop"
        self.notifier.notify('startup')
        try:
            self.watcher.watch()
        except KeyboardInterrupt:
            print 'shutting down'
        self.notifier.notify('shutdown')


def dynload(path):
    "dyanmic import utility"
    path_parts = path.split('.')
    if len(path_parts) == 1:
        raise ValueError
    module_name = '.'.join(path_parts[:-1])
    module = __import__(module_name, {}, {}, path_parts[-1])
    return getattr(module, path_parts[-1])


def main(argv):
    usage = "usage: %prog -c command [-m mask] -d directory"
    parser = OptionParser(usage=usage, version="%prog " + __version__)
    parser.add_option("-c", "--command",
                    help="command to run upon detection of a changed file"),
    parser.add_option("-d", "--directory", action="append",
                    help="directories to watch for changes (default=cwd)"),
    parser.add_option("-i", "--ignore", action="append",
                    help="directories to ignore for changes")
    parser.add_option("-m", "--mask",
                    help="file mask required to trigger command (default=no mask)")
    parser.add_option("--watcher",
                    help="python path to watcher (default=mutter.ModTimeWatcher)")
    parser.add_option("--notifier",
                    help="python path to watcher (default=mutter.SoundNotifier)")
    parser.add_option("--responder",
                    help="python path to responder (default=mutter.DeltaThresholdResponder)")

    parser.set_defaults(directories=[], ignore=[], mask='*', \
        watcher = 'mutter.ModTimeWatcher',
        responder = 'mutter.DeltaThresholdResponder',
        notifier = 'mutter.SoundNotifier',
    )

    (options, args) = parser.parse_args()

    if len(options.directories) == 0:
        options.directories = ['.']

    mutter = Mutter(options)
    mutter.run()

if __name__ == "__main__":
    main(sys.argv[1:])
