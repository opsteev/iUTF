from ilog import log, Ilogger
from dev import *
import re

__all__ = ['ExceptionIAP', 'IAP']

class ExceptionIAP(Exception):
    '''Raised for IAP exceptions.
    '''

class IAP(Device):
    def __init__(self, device_name, mgt_method, hostname=None, customized_mode = False, *args, **kwargs):
        self.device_name = device_name
        self.mgt_method = mgt_method
        self.hostname = hostname
        self.customized_mode = customized_mode

        self.support_password = r'S1erraOn#'
        self.username = kwargs.get('username', 'admin')
        self.password = kwargs.get('password', 'admin')

        '''
        Initialize the Device
        '''
        Device.__init__(self, device_name, mgt_method, *args, **kwargs)

        if not customized_mode:
            self.support_mode = 'support'
            self.cli_mode = 'cli'
            self.config_mode = 'config'
            self.config_deep_mode = 'config_deep'
            self.apboot_mode = 'apboot'
            self.apboot_entrance_mode = 'apboot_entrance'
            self.support_password_mode = 'support_password'
            self.type_username_mode = 'type_username'
            self.type_password_mode = 'type_password'

            self.add_mode(self.type_username_mode, 'User:')
            self.add_mode(self.type_password_mode, 'Password:')
            self.add_mode(self.support_mode, r'~ \#[\s]*$')
            self.add_mode(self.cli_mode, r'%s\#[\s]*$' % 
                (hostname or r'[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}'))
            self.add_mode(self.config_mode, r'%s \(config\) \#[\s]*$' % 
                (hostname or r'[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}'))
            self.add_mode(self.config_deep_mode, r'%s \(((?!config).)+\) \#[\s]*$' % 
                (hostname or r'[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}'))
            self.add_mode(self.apboot_mode,r'apboot>[\s]*$')
            self.add_mode(self.apboot_entrance_mode, r'Hit <enter>')
            self.add_mode(self.support_password_mode, r'support\r\nPassword:')

            self.add_path(self.type_username_mode, self.type_password_mode, self.username)
            self.add_path(self.type_password_mode, self.cli_mode, self.password)
            self.add_path(self.cli_mode, self.support_password_mode, 'support')
            self.add_path(self.support_password_mode, self.support_mode, self.support_password)
            self.add_path(self.support_mode, self.cli_mode, 'exit')
            self.add_path(self.cli_mode, self.config_mode, 'configure terminal')
            self.add_path(self.config_mode, self.cli_mode, 'exit')
            self.add_path(self.config_deep_mode, self.cli_mode, 'end')
            self.add_path(self.support_mode, self.apboot_entrance_mode, 'reboot', timeout=120)
            self.add_path(self.cli_mode, self.apboot_entrance_mode, 'reload', timeout=120)
            self.add_path(self.apboot_entrance_mode, self.apboot_mode, '\r')
            self.add_path(self.apboot_mode, self.type_username_mode, 'reset')

    def __eq__(self, obj):
        return self.device_name == obj.device_name

    def cfg(self, cmds, per_ap = False):
        '''
        Send configuration to IAP, 
        if per_ap setting is True, switch to cli mode and write memory at last.
        if the configuration is for global ap, switch to config mode and commit apply at last.
        '''
        if per_ap:
            self.to_mode(self.cli_mode)
            self.cmd(cmds, timeout=30)
            self.cmd('write memory', timeout=30)
        else:
            self.to_mode(self.config_mode)
            self.cmd(cmds, timeout=30)
            self.to_mode(self.cli_mode)
            self.cmd('commit apply', timeout=30)

    @staticmethod
    def show_table_parser(show_log):
        '''
        Parse the show table.
        '''
        show_lines = [line.strip() for line in show_log.splitlines() if len(line.strip()) != 0]
        if len(show_lines) == 0:
            return None
        tables = {}
        in_table = False
        parsing_fields = False
        table_rows = []
        table_name = None
        while len(show_lines) != 0:
            cur = show_lines.pop(0)
            next = show_lines[0] if len(show_lines) != 0 else ''

            if in_table:
                if parsing_fields:
                    
                    row_list = IAP._get_fields(cur,fields_len)
                    # Handle strange lines, however I think it is not easy to hit this condition
                    while len(row_list) < len(fields_title):
                        row_list = row_list + ['',]
                    log.debug('row list: %r' % row_list)
                    if not re.match('^-+[\s]+[\s-]+-$', cur):
                        table_rows.append(row_list)

                    if len(next) < min_line_len:
                        log.debug('The next hits this condition 1: %r' % next)
                        log.debug('condition 1, current line     : %r' % cur)
                        parsing_fields = False
                    else:
                        b = [ a for a in IAP._get_fields(next, fields_len) if a[0] == ' ']
                        if len(b) != 0:
                            parsing_fields = False
                            log.debug('The next hits this condition 2: %r' % next)
                            log.debug('condition 2, current line     : %r' % cur)
                    if not parsing_fields:
                        d = {}
                        for a in zip(*table_rows):
                            d[a[0]] = a[1:]
                        if tables.has_key(table_name):
                            tables[table_name].update(d)
                        else:
                            tables[table_name] = d
                        in_table = False
                        table_name = None

                elif re.match('^-+[\s]+[\s-]+-$', next):
                    fields_len = map(lambda y: len(y), filter(lambda x: x!='', re.split('(-+\s+)', next)))
                    # Get fields title
                    fields_title = IAP._get_fields(cur, fields_len)
                    log.debug('fields tilte %r' % fields_title)
                    table_rows.append(fields_title)
                    parsing_fields = True
                    hyphen_line_len = len(next)
                    min_line_len = len(next) - fields_len[-1]

            # Find out the table name:
            # If the next line of table is combined by '-',
            # I assume that the current line should be the table name
            elif re.match('^-+$', next):
                table_name = cur
                in_table = True
                log.debug('table name %r' % table_name)
            # colon format line, no need to check next line
            elif ':' in cur:
                colon_row_list = cur.split(':', 1)
                tables[colon_row_list[0].strip()] = colon_row_list[1]
            cur = next
            # end while
        log.debug('tables %r' % tables)
        return tables

    @staticmethod
    def _get_fields(line, fields_len):
        src = 0
        fields = []
        for f in fields_len[:-1]:
            fields.append(line[src: src+f].rstrip())
            src = src + f
        fields.append(line[src:].rstrip())
        return fields

    @staticmethod
    def get_master(*handles):
        '''
        Get the master handle in the cluster
        Note: There should be only one master
        '''
        master_count = 0
        master = None
        for handle in handles:
            handle.to_mode(handle.cli_mode)
            ret = handle.cmd('show summary | inc "Master IP"')
            if '*' in ret:
                master_count += 1
                master = handle
        if master_count != 1:
            return None
        else:
            return master

    @staticmethod
    def get_conf_template(module, *args, **kwargs):
        pass

    @staticmethod
    def get_conf_ssid(ssid, edit=False, *args, **kwargs):
        cmd_head = 'wlan ssid-profile "%s"' % ssid
        cmd_end = 'exit'
        command = []
        command.append(cmd_head)
        default_arg = ['enable']
        default_kwarg = {'type': 'employee', 
                         'essid': ssid,
                         'max-authentication-failures': '0',
                         'dmo-channel-utilization-threshold': '90',
                         'local-probe-req-thresh': '0',
                         'max-clients-threshold': '64',
                         'inactivity-timeout': '1000',
                         'rf-band': 'all',
                         'broadcast-filter': 'arp'
        }
        if edit:
            command.extend(args)
            for k,v in kwargs.items():
                command.append("%s %s"%(k, v))
        else:
            if args:
                command.extend(set(default_arg.extend(args)))
            else:
                command.extend(default_arg)
            kwp = default_kwarg.copy()
            kwp.update(kwargs)
            for k,v in kwp.items():
                command.append("%s %s"%(k, v))
            if 'set-role' not in args or 'set-role' not in kwargs.keys():
                command.append("set-role-unrestricted")
        command.append(cmd_end)

        return '\n'.join(command)

    @staticmethod
    def get_conf_auth_server(server_name, edit=False, *args, **kwargs):
        cmd_head = 'wlan auth-server "%s"' % server_name
        cmd_end = 'exit'
        command = []
        command.append(cmd_head)
        default_arg = []
        default_kwarg = {}
        if edit:
            command.extend(args)
            for k,v in kwargs.items():
                command.append("%s %s"%(k, v))
        else:
            if args:
                command.extend(set(default_arg.extend(args)))
            else:
                command.extend(default_arg)
            kwp = default_kwarg.copy()
            kwp.update(kwargs)
            for k,v in kwp.items():
                command.append("%s %s"%(k, v))
        command.append(cmd_end)

        return '\n'.join(command)

    def get_bssid(self, ssid, band='a'):
        self.to_mode(self.cli_mode)
        ret = self.cmd('show ap bss-table')
        ret_dict = IAP.show_table_parser(ret)
        ssid_idxes = [i for i in range(len(ret_dict['Aruba AP BSS Table']['ess'])) if ret_dict['Aruba AP BSS Table']['ess'][i]==ssid]
        bssid_idx = [i for i in ssid_idxes if band in ret_dict['Aruba AP BSS Table']['phy'][i]]
        if len(bssid_idx) != 1:
            self.error('Find bssid failed for ssid %s' % ssid)
            return False
        else:
            return ret_dict['Aruba AP BSS Table']['bss'][bssid_idx[0]]

