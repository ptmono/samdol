#!/usr/bin/python
# coding: utf-8

'''
$ samdolcd.py start|stop|restart


'''

import config
import samdolc
from daemon import runner

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'

        # self.stdout_path = '/dev/tty'
        # self.stderr_path = '/dev/tty'
        self.pidfile_path = config.daemon_pid_file_path
        self.pidfile_timeout = 5

    def run(self):
        samdolc.main()

def main():
    try:
        app = App()
        daemon_runner = runner.DaemonRunner(app)
        daemon_runner.do_action()
    except Exception, err:
        config.logger.debug(repr(err))

if __name__ == "__main__":
    main()

