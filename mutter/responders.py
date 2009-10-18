import subprocess

class BaseResponder(object):
    def __init__(self, notifier, command):
        self.notifier = notifier
        self.command = command

    def handle_output(self, output):
        for line in output:
            print line,

    def command_succeeded(self, output, return_value):
        self.notifier.notify('green')

    def command_failed(self, output, return_value):
        self.notifier.notify('red')

    def run_user_command(self):
        command = self.command
        #should_interpolate = command.find('%s') > 0
        #if should_interpolate:
        #    command = command % path

        print 'running: %s' % command
        p = subprocess.Popen(command.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        p.stdin.close()
        return_value = p.wait()
        output = p.stdout.readlines()
        p.stdout.close()

        self.handle_output(output)

        if return_value == 0:
            callback = self.command_succeeded
        else:
            callback = self.command_failed

        callback(output, return_value)

    def respond(self, changes):
        if self.should_respond(changes):
            self.notifier.notify('run')
            self.run_user_command()

class DeltaThresholdResponder(BaseResponder):
    def __init__(self, notifier, command):
        super(DeltaThresholdResponder, self).__init__(notifier, command)
        self.modification_time_delta = 0
        self.modification_time_threshold = 2

    def should_respond(self, changes):
        self.modification_time_delta += max(changes, key=lambda c: c[2])[2]
        if self.modification_time_delta >= self.modification_time_threshold:
            self.modification_time_delta = 0
            return True
