from pexpect import *
import time

from ilog import *

__all__ = ['ExceptionSSH', 'ExceptionTelnet', 'SSH', 'Telnet']

class ExceptionSSH(ExceptionPexpect):
    '''Raised for SSH exceptions.
    '''

class ExceptionTelnet(ExceptionPexpect):
    '''Raised for Telnet exceptions.
    '''

class SSH(spawn):
    def __init__ (self, timeout=30, maxread=2000, searchwindowsize=None,
                    logfile=None, cwd=None, env=None, ignore_sighup=True, echo=True,
                    encoding=None, codec_errors='strict',
                    host='', port='22', username='', password='', options='', prompt='[#$]', logger=None):

        # self.logfile = FileAdapter(logger)

        spawn.__init__(self, None, timeout=timeout, maxread=maxread,
                       searchwindowsize=searchwindowsize, logfile=logfile,
                       cwd=cwd, env=env, ignore_sighup=ignore_sighup, echo=echo,
                       encoding=encoding, codec_errors=codec_errors)
        self.logfile_read = FileAdapter(logger)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh_opts = options or "-o 'StrictHostKeyChecking=no' -o 'UserKnownHostsFile /dev/null'"
        self.prompt = prompt
        self.logger = logger
        self.connected = False
    def connect(self):
        cmd = "ssh %s -p %s %s@%s" % (self.ssh_opts, self.port, self.username, self.host)
        spawn._spawn(self, cmd)
        while True:
            idx = self.expect([self.prompt, "No route to host", "timed out", "refused", "assword:", 
                "\(yes/no\)", "\(y/n\)", EOF, TIMEOUT])
            if idx == 0:
                self.connected = True
                break
            elif idx in (1, 2, 3):
                self.close()
                break
            elif idx == 4:
                self.sendline(self.password)
            elif idx == 5:
                self.sendline('yes')
            elif idx == 6:
                self.sendline('y')
            else:
                self.close()
                break
        time.sleep(0.1)
        return self.isalive()
    def disconnect(self):
        self.terminate(True)
        self.close()
        self.connected = 0
    def is_connected(self):
        self.connected = self.isalive()
        return self.connected

class Telnet(spawn):
    def __init__ (self, timeout=30, maxread=2000, searchwindowsize=None,
                    logfile=None, cwd=None, env=None, ignore_sighup=True, echo=True,
                    encoding=None, codec_errors='strict',
                    host='', port='23', username='', password='', prompt='[#$>]', logger=None, console=False):
        
        #self.logfile = FileAdapter(logger)

        spawn.__init__(self, None, timeout=timeout, maxread=maxread,
                       searchwindowsize=searchwindowsize, logfile=logfile,
                       cwd=cwd, env=env, ignore_sighup=ignore_sighup, echo=echo,
                       encoding=encoding, codec_errors=codec_errors)
        self.logfile_read = FileAdapter(logger)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.prompt = prompt
        self.logger = logger
        self.connected = False
        self.console = console
    def connect(self):
        cmd = "telnet %s %s" % (self.host, self.port)
        spawn._spawn(self, cmd)
        if self.console:
            self.connected = True
            return self.connected
        while True:
            idx = self.expect([self.prompt, "No route to host", "timed out", "closed by foreign host", "assword:", 
                "ogin:", "User:", EOF, TIMEOUT])
            if idx == 0:
                self.connected = True
                break
            elif idx in (1, 2, 3):
                self.close()
                break
            elif idx == 4:
                self.sendline(self.password)
            elif idx == 5:
                self.sendline(self.username)
            elif idx == 6:
                self.sendline(self.username)
            else:
                self.close()
                break
        time.sleep(0.1)
        return self.isalive()
    def disconnect(self):
        self.terminate(True)
        self.close()
        self.connected = 0
    def is_connected(self):
        self.connected = self.isalive()
        return self.connected
