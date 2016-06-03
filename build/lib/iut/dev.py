from cli import *
from ilog import log, Ilogger
from dijkstra import shortestPath

from pexpect import EOF, TIMEOUT, spawn

__all__ = ['ExceptionDevice', 'Device']

class ExceptionDevice(Exception):
    '''Raised for Device exceptions.
    '''

class Device(SSH, Telnet):
    def __init__(self, device_name, mgt_method, *args, **kwargs):
        self.device_name = device_name
        self.mgt_method = mgt_method

        self.modes = {}

        self.graph = {}
        self.path_cmd = {}

        self.auto_response = {}

        self.max_timeout = 30

        kwargs['logger'] = Ilogger(device_name)
        self.logger = kwargs['logger']

        self.prompt = kwargs.get('prompt', '[#$>]')

        if not self.device_name:
            raise ExceptionDevice('Unknown device NAME')
        if self.mgt_method.lower() == 'ssh':
            # SSH.__init__(self, timeout=kwargs.get('timeout', 30), maxread=kwargs.get('maxread', 2000), 
            #         searchwindowsize=kwargs.get('searchwindowsize', None), logfile=kwargs.get('logfile', None), 
            #         cwd=kwargs.get('cwd', None), env=kwargs.get('env', None), ignore_sighup=kwargs.get('ignore_sighup', None), 
            #         echo=kwargs.get('echo', None), encoding=kwargs.get('encoding', None), 
            #         codec_errors=kwargs.get('codec_errors', 'strict'),
            #         host=kwargs.get('host', ''), port=kwargs.get('port', '22'), 
            #         username=kwargs.get('username', ''), password=kwargs.get('password', ''), 
            #         options=kwargs.get('options', ''), prompt=kwargs.get('prompt', '[#$]'), logger=kwargs.get('logger', None))
            self.logger.debug('Connect via ssh')
            SSH.__init__(self, *args, **kwargs)
        elif self.mgt_method.lower() == 'telnet':
            # Telnet.__init__(self, timeout=kwargs.get('timeout', 30), maxread=kwargs.get('maxread', 2000), 
            #         searchwindowsize=kwargs.get('searchwindowsize', None), logfile=kwargs.get('logfile', None), 
            #         cwd=kwargs.get('cwd', None), env=kwargs.get('env', None), ignore_sighup=kwargs.get('ignore_sighup', None), 
            #         echo=kwargs.get('echo', None), encoding=kwargs.get('encoding', None), 
            #         codec_errors=kwargs.get('codec_errors', 'strict'),
            #         host=kwargs.get('host', ''), port=kwargs.get('port', '23'), 
            #         username=kwargs.get('username', ''), password=kwargs.get('password', ''), 
            #         prompt=kwargs.get('prompt', '[#$>]'), logger=kwargs.get('logger', None))
            self.logger.debug('Connect via telnet')
            Telnet.__init__(self, *args, **kwargs)
        else:
            raise ExceptionDevice('Unknown MGT-METHOD for %s' % self.device_name)

    def connect(self):
        if self.mgt_method.lower() == 'ssh':
            self.logger.info('Connect via ssh')
            return SSH.connect(self)
        elif self.mgt_method.lower() == 'telnet':
            self.logger.info('Connect via telnet')
            return Telnet.connect(self)
        else:
            raise ExceptionDevice('Unknown MGT-METHOD for %s' % self.device_name)

    def disconnect(self):
        if self.mgt_method.lower() == 'ssh':
            return SSH.disconnect(self)
        elif self.mgt_method.lower() == 'telnet':
            return Telnet.disconnect(self)
        else:
            raise ExceptionDevice('Unknown MGT-METHOD for %s' % self.device_name)
    
    def is_connected(self):
        if self.mgt_method.lower() == 'ssh':
            return SSH.is_connected(self)
        elif self.mgt_method.lower() == 'telnet':
            return Telnet.is_connected(self)
        else:
            raise ExceptionDevice('Unknown MGT-METHOD for %s' % self.device_name)

    def add_mode(self, mode, pattern):
        '''
        Add mode for device, pattern is the prompt of the mode.
        '''
        self.modes[pattern] = mode

    def add_path(self, source, destination, cmd,timeout = 30):
        '''
        Provide the path from source mode to destination mode.
        source: source mode
        destination: destination mode
        timeout: the expect timeout for the path
        '''
        self.max_timeout = max(self.max_timeout, timeout)
        if self.graph.has_key(source):
            self.graph[source].update({destination: timeout})
        else:
            self.graph[source] = {destination: timeout}
        self.path_cmd[(source, destination)] = cmd

    def add_auto_response(self, pattern, cmd):
        '''
        if expect the pattern, cmd will be sent automatically.
        '''
        self.auto_response[pattern] = cmd

    def cmd(self, cmds, *args, **kwargs):
        '''
        send commands in this spawn session.
        '''
        tmp_cmd_list = cmds.splitlines()
        without_waiting = kwargs.get('without_waiting', False)
        get_mode = kwargs.get('get_mode', False)
        prompt = kwargs.get('prompt', None)
        action = kwargs.get('action', None)
        p_a_keypair = dict(zip(prompt, action)) if prompt else None
        cur_mode = None
        cur_buffer = ''
        cmd_list = [cmd.strip() for cmd in tmp_cmd_list if len(cmd.strip()) != 0 and cmd.strip()[0] != '#'] if not get_mode else ['',]
        log.debug('cmd_list %r' % cmd_list)
        exps = self.auto_response.keys() + self.modes.keys() + [EOF, TIMEOUT] if not prompt else self.auto_response.keys() + prompt + [EOF, TIMEOUT]
        for cmd in cmd_list:
            self.sendline(cmd)
            while True:
                idx = self.expect(exps, timeout = kwargs.get('timeout', self.max_timeout))
                if idx < len(self.auto_response):
                    cur_buffer = cur_buffer + self.before
                    self.sendline(self.auto_response[exps[idx]])
                elif prompt and idx < len(self.auto_response) + len(prompt):
                    cur_buffer = cur_buffer + self.before
                    if p_a_keypair[exps[idx]]:
                        self.sendline(p_a_keypair[exps[idx]])
                        continue
                    break
                elif prompt is None and idx < len(self.auto_response) + len(self.modes):
                    cur_mode = self.modes[exps[idx]]
                    cur_buffer = cur_buffer + self.before
                    break
                elif idx == len(exps) - 1:
                    cur_buffer = cur_buffer + self.before
                    raise ExceptionDevice('Timeout to hit any prompt. current buffer: \n%s\n' % cur_buffer)
                else:
                    raise ExceptionDevice('EOF')
        return cur_mode if get_mode else cur_buffer

    def get_cur_mode(self):
        '''
        Return the current mode.
        '''
        return self.cmd('', get_mode=True)

    def to_mode(self, mode):
        '''
        Get to the mode which you want to arive, use the dijkstra algorithm to find
        the shortest path.
        '''
        cur_mode = self.get_cur_mode()
        path = shortestPath(self.graph, cur_mode, mode)
        if len(path) != 1:
            cur = path.pop(0)
            while len(path) != 0:
                next = path.pop(0)
                self.cmd(self.path_cmd[(cur, next)])
                cur = next
                cur_mode = cur
        return cur_mode

