import os
import platform
import subprocess

class SoundPlayer:
    """Simple audio file player, invokes afplay on macs, mpg123 otherwise."""
    def __init__(self):
        self.basedir = os.path.dirname(__file__)
        self.sounds = {
            'startup': 'run.mp3',
            'shutdown': 'quit.mp3',
            'run': 'run_command.mp3',
            'red': 'red.mp3',
            'green': 'green.mp3'
        }

        self.player = 'mpg123'
        if platform.system == 'Darwin':
            self.player = 'afplay'

    def play(self, name):
        if name not in self.sounds:
            print 'sound "%s" not found in mapping' % name
        sound_file = os.path.join(self.basedir, 'sounds', self.sounds[name])
        subprocess.call([self.player, '-q', sound_file], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

class BaseNotifier(object):
    "Notifiers need only to implement notify"
    def notify(self, event):
        raise NotImplementedError()

class TextNotifier(object):
    "Basic text notifier"
    def notify(self, event):
        print 'Notify: ', event

class SoundNotifier(object):
    "Simple notifier that uses SoundPlayer"
    def __init__(self):
        self.player = SoundPlayer()

    def notify(self, event):
        if event in self.player.sounds:
            self.player.play(event)
