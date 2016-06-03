from ilog import *
from dev import *

class MacOS(Device):
    def __init__(self, device_name, mgt_method, customized_mode = False, *args, **kwargs):
        self.device_name = device_name
        self.mgt_method = mgt_method

        '''
        Initialize the Device
        '''
        Device.__init__(self, device_name, mgt_method, *args, **kwargs)
        if not customized_mode:
            self.user_mode = 'user_mode'
            self.root_mode = 'root_mode'
            self.su_root_password = 'su_root_password'
            self.root_password = kwargs.get('root_password', '123456')
            self.add_mode(self.user_mode, r'[^\r\n]+[\s]*\$[\s]*$')
            self.add_mode(self.root_mode, r'[^\r\n]+[\s]*\#[\s]*$')
            self.add_mode(self.su_root_password, r'su - root\r\nPassword:')
            self.add_path(self.user_mode, self.su_root_password, r'su - root')
            self.add_path(self.su_root_password, self.root_mode, self.root_password)
            self.add_path(self.root_mode, self.user_mode, r'exit')

    def sudo(self, cmd, *args, **kwargs):
        self.cmd('sudo %s'%cmd, prompt = ['Password:', '\$'], action = [self.password, None])

