#!/usr/bin/env python
"""Test Notifier

Plays sounds and renders notifications based on the result of a command run
when files are modified.

See --help for usage.
"""

__author__ = "Travis Cline (travis.cline@gmail.com)"
__version__ = "$Revision$"
__date__ = "$Date$"

import os, sys, time, pynotify, pygtk
from optparse import OptionParser
from pyinotify import WatchManager, Notifier, EventsCodes, ProcessEvent
pygtk.require('2.0')

class PathWatcher(ProcessEvent):
	"""plays sounds and notifications based on events"""

	def __init__(self, TestNotifier):
		self.TestNotifier = TestNotifier;

	def process_IN_CREATE(self, event):
		print "Create: %s" %  os.path.join(event.path, event.name)

	def process_IN_DELETE(self, event):
		print "Remove: %s" %  os.path.join(event.path, event.name)
	
	def process_IN_IGNORED(self, event):
		pass
	
	def process_IN_MODIFY(self, event):
		print "Modified: %s" %  os.path.join(event.path, event.name)
		self.TestNotifier.fileModified(os.path.join(event.path, event.name))

class SoundPlayer:
	def __init__(self, files=None):
		self.basedir = os.path.dirname(sys.argv[0])
		self.sounds = {
			'startup': '/sounds/run.mp3',
			'shutdown': '/sounds/quit.mp3',
			'run': '/sounds/run_command.mp3',
			'red': '/sounds/red.mp3',
			'green': '/sounds/green.mp3'
		}
		self.player = '/usr/bin/mpg123'

	def playSound(self, name):
		print 'playing sound for ' + name
		pid = os.spawnl(os.P_WAIT, self.player, '', '-q', self.basedir + self.sounds[name])

class TestNotifier:
	"""plays sounds and renders notifications based on file events"""

	def __init__(self, options):
		self.setOptions(options)
		self.initWatcher()
		self.initNotifier()
		self.initSoundPlayer()
		self.lastModifiedTime = 0
		
		self.soundPlayer.playSound('startup')
		print 'ready'
	
	def initWatcher(self):
		self.watchManager = WatchManager()
		self.pathWatcher = PathWatcher(self)
		self.notifier = Notifier(self.watchManager, self.pathWatcher)
		
		eventMask = EventsCodes.IN_DELETE | EventsCodes.IN_CREATE | EventsCodes.IN_MODIFY
		
		for path in self.options['watch']:
			print 'watching %s' % os.path.abspath(path)
			wdd = self.watchManager.add_watch(os.path.abspath(path), eventMask, rec=True, auto_add=True)

			for ignoredPath in self.options['ignore']:
				ignoredPath = os.path.abspath(ignoredPath)
				if ignoredPath in wdd:
					print 'ignoring %s' % ignoredPath
					self.watchManager.rm_watch(wdd[os.path.abspath(ignoredPath)], rec=True)

	def initNotifier(self):
		if not pynotify.init("Basics"):
			print "Failed to initialize pynotify"
			sys.exit(1)

	def initSoundPlayer(self):
		self.soundPlayer = SoundPlayer()

	def mainLoop(self):
		while True:  # loop forever
			try:
				# process the queue of events as explained above
				self.notifier.process_events()
				if self.notifier.check_events():
					# read notified events and enqeue them
					self.notifier.read_events()
				# you can do some tasks here...
			except KeyboardInterrupt:
				# destroy the inotify's instance on this interrupt (stop monitoring)
				self.notifier.stop()
				self.soundPlayer.playSound('shutdown')
				break
	
	def fileModified(self, path):
		print time.time() - self.lastModifiedTime
		if (time.time() - self.lastModifiedTime) < 1 :
			return
		else:
			self.lastModifiedTime = time.time()

		self.soundPlayer.playSound('run')
		
		command = self.options['command']
		should_interpolate = command.find('%s') > 0
		if should_interpolate:
			command = command % path
		print 'running: %s' % command
		returnValue = os.system(command)
		
		if returnValue == 0:
			callback = self.commandSucceeded
		else:
			callback = self.commandFailed
		
		callback(path)
	
	def commandSucceeded(self, path):
		icon = 'file:///usr/share/icons/Tango/scalable/status/dialog-information.svg'
		self.showNotification('Tests Passed','File Modified: %s' % path, icon)
		self.soundPlayer.playSound('green')
	
	def commandFailed(self, path):
		icon = 'file:///usr/share/icons/Tango/scalable/status/dialog-error.svg'
		self.showNotification('Tests Failed','File Modified: %s' % path, icon)
		self.soundPlayer.playSound('red')

	def showNotification(self, summary, body, icon):
		n = pynotify.Notification(summary, body, icon)
		n.add_action("ok", "OK", self.callbackOk)
		n.show()
		
	def callbackOk(self):
		pass

	def setOptions(self, options):
		self.options = {'command': options.command,
						'watch': options.watch,
						'ignore': options.ignore,
						'mask': options.mask}

def main(argv):
	usage = "usage: %prog -c command [-m mask] -w directory"
	parser = OptionParser(usage=usage, version="%prog " + __version__)
	parser.add_option("-c", "--command",
					help="command to run upon detection of a changed file"),
	parser.add_option("-w", "--watch", action="append",
					help="directories to watch for changes (default=cwd)"),
	parser.add_option("-i", "--ignore", action="append",
					help="directories to ignore for changes")
	parser.add_option("-m", "--mask",
					help="file mask required to trigger command (default=no mask)")
	parser.set_defaults(watch=[], ignore=[], mask='*')

	(options, args) = parser.parse_args()

	if len(options.watch) == 0:
		options.watch = ['.']

	tn = TestNotifier(options)
	tn.mainLoop()

if __name__ == "__main__":
	main(sys.argv[1:])
