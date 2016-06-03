from ilog import *
from dev import *
from constant import WIN_WIRELESS_XML
from os.path import join

class ExceptionWin(Exception):
    '''Raised for Win exceptions.
    '''

class Win(Device):
    def __init__(self, device_name, mgt_method, customized_mode = False, *args, **kwargs):
        self.device_name = device_name
        self.mgt_method = mgt_method

        '''
        Initialize the Device
        '''
        Device.__init__(self, device_name, mgt_method, *args, **kwargs)
        if not customized_mode:
            self.login_mode = 'login_mode'
            self.add_mode(self.login_mode, r'[^\r\n]+[\s]*[\$\>][\s]*$')

    def get_ipconfig_all(self):
        '''
        It will push command ipconfig /all, and return dict for this command.
        e.g:
        a = Win(...)
        ret = a.get_ipconfig_all():
        ret = {'Ethernet adapter Local Area Connection': {
                    'Description': 'Intel(R) Ethernet Connection (3) I218-LM',
                    'Physical Address': '34-E6-D7-7B-26-98',
                    'IPv4 Address': '10.65.10.186(Preferred)',
                    ...
                    },
               'Wireless LAN adapter Wireless Network Connection': {
                    'Description': 'Intel(R) Dual Band Wireless-AC 7265',
                    'Physical Address': '5C-E0-C5-06-CE-0D',
                    ...
               },
               ...
              }

        '''
        ret = self.cmd('ipconfig /all')
        ipconfig = {}
        lines = [line.rstrip() for line in ret.splitlines() if line.rstrip() != '']
        for line in lines:
            if line[0] != " ":
                table_header = line
                ipconfig[table_header] = {}
            else:
                table_ctx = line.strip().split(':', 1)
                ipconfig[table_header].update({table_ctx[0].rstrip('.'): table_ctx[1]})
        return ipconfig

    def get_ipconfig(self, interface='Wireless Network Connection'):
        '''
        Get ipconfig for specific interface, default is 'Wireless Network Connection'
        If return None, it means getting failed.
        '''
        ret = self.get_ipconfig_all()
        for k in ret.keys():
            if interface in k:
                return ret[k]
        return None

    def ping(self, host, count=5, timeout=120, pass_rate=80, extra=""):
        '''
        host: the destination for ping
        count: the count of ping packets
        timeout: the timeout for this process
        pass_rate: the pass rate for ping
        extra: extra parameters which will be passed to ping directly
        '''
        if count <=0:
            raise ExceptionWin("count for ping should be greater than 0")
        command = "ping %s -n %d %s" % (host, count, extra)
        ret = self.cmd(command, timeout=timeout)
        return ret.count("bytes=")*100/count >= pass_rate
    #-----------
    # For the below api, we have the below requirments:
    # * The tool client.exe, and default, we put it into the path c:/client1
    # * Cygwin
    #-----------
    def gen_xml_file(self, **kwargs):
        '''
        It uses to generate the xml file for netsh wlan or the tool client.exe which could be
        used to connect to WIFI.
        It has the below parameter, * is mandatory, other is optional:
        * ssid: ssid name
        profilename: Profile name in for the xml file, default value equal to ssid
        authentication: the authentication method. The value should be one of the below. default is open
                        open: for open ssid.
                        static-wep: static wep
                        dynamic-wep: wep with dot1x
                        wpa-psk: wpa psk
                        wpa2-psk: wpa2 psk
                        wpa: wpa enterprise
                        wpa2: wpa2 enterprise
        eap: the eap method for dot1x authentication:
            peap-gtc: peap gtc
            peap-mschapv2: peap mschapv2
            tls: tls

            * Note: Because windows clients do not support ttls as default if no additional driver, so we do not
                    provide the api for it.

        wep_key: Use for static-wep
        wep_key_index: Use for static-wep

        username: username for dot1x authentication, this is required for peap authentication
        password: password for dot1x authentication or psk
            * Note: If we just provide the password without username, we would use it as psk

        certname: the certificate name for your tls authentication, you must install this certificate to the client first
        thumbprint: the sha1 fingerprint/thumbprint for your certificate

        dest: the destination path for this xml file, because the default tool client.exe will be put into c:/client1, so
                the dest default value is c:/client
        '''
        if not kwargs.get('ssid'):
            raise ExceptionWin('You must provide ssid parameter for this function')
        ssid = kwargs['ssid']
        profilename = kwargs.get('profilename', kwargs['ssid'])
        xml_file_name = '%s.xml' % profilename
        user_xml_file_name = 'user_%s.xml' % profilename
        dest_path = kwargs.get('dest', 'c:/client')
        authentication = kwargs.get('authentication', 'open')
        eap = kwargs.get('eap', 'peap-mschapv2')
        username = kwargs.get('username')
        password = kwargs.get('password')
        certname = kwargs.get('certname')
        thumbprint = kwargs.get('thumbprint')
        wep_key = kwargs.get('wep_key')
        wep_key_index = kwargs.get('wep_key_index')

        # make sure the xml file should be deleted first
        self.cmd('rm -rf %s' % join(dest_path, xml_file_name))
        self.cmd('rm -rf %s' % join(dest_path, user_xml_file_name))

        used_xml = ''
        used_user_xml = ''
        if authentication == 'open':
            used_xml = WIN_WIRELESS_XML['OPEN']
            used_xml = used_xml.replace('AUTHENTICATION', 'open')
            used_xml = used_xml.replace('ENCRYPTION', 'none')
        elif authentication == 'static-wep':
            used_xml = WIN_WIRELESS_XML['WEP-STATIC']
            if not wep_key_index or not wep_key:
                raise ExceptionWin('wep_key and wep_key_index are required for static-wep')
            used_xml = used_xml.replace('WEPKEY_INDEX', wep_key_index)
            used_xml = used_xml.replace('WEP-KEY', wep_key)
            used_xml = used_xml.replace('AUTHENTICATION', 'open')
            used_xml = used_xml.replace('ENCRYPTION', 'WEP')
        elif authentication == 'wpa-psk':
            used_xml = WIN_WIRELESS_XML['WPA-PSK']
            used_xml = used_xml.replace('WPA_PSK', password)
            used_xml = used_xml.replace('AUTHENTICATION', 'WPA')
            used_xml = used_xml.replace('ENCRYPTION', 'TKIP')
        elif authentication == 'wpa2-psk':
            used_xml = WIN_WIRELESS_XML['WPA2-PSK']
            used_xml = used_xml.replace('WPA2_PSK', password)
            used_xml = used_xml.replace('AUTHENTICATION', 'WPA2')
            used_xml = used_xml.replace('ENCRYPTION', 'AES')
        elif eap:
            if authentication == 'wpa':
                used_xml = used_xml.replace('AUTHENTICATION', 'WPA')
                used_xml = used_xml.replace('ENCRYPTION', 'TKIP')
            elif authentication == 'wpa2':
                used_xml = used_xml.replace('AUTHENTICATION', 'WPA2')
                used_xml = used_xml.replace('ENCRYPTION', 'AES')
            elif authentication == 'dynamic-wep':
                used_xml = used_xml.replace('AUTHENTICATION', 'OPEN')
                used_xml = used_xml.replace('ENCRYPTION', 'WEP')
            if eap == 'peap-mschapv2':
                used_xml = WIN_WIRELESS_XML['PEAP-MSCHAPV2']
                used_user_xml = WIN_WIRELESS_XML['MSCHAPV2-USER']
                if not username or not password:
                    raise ExceptionWin('username and password are required for peap-mschapv2')
                used_user_xml = used_user_xml.replace('USERNAME', username)
                used_user_xml = used_user_xml.replace('PASSWORD', password)
            elif eap == 'peap-gtc':
                used_xml = WIN_WIRELESS_XML['PEAP-GTC']
                if not username or not password:
                    raise ExceptionWin('username and password are required for peap-gtc')
                used_xml = used_xml.replace('USERNAME', username)
                used_xml = used_xml.replace('PASSWORD', password)
            elif eap == 'tls':
                used_xml = WIN_WIRELESS_XML['TLS']
                used_user_xml = WIN_WIRELESS_XML['TLS-CERT']
                if not certname or not thumbprint:
                    raise ExceptionWin('certname and thumbprint are required for tls')
                used_user_xml = used_user_xml.replace('CERTNAME', certname)
                used_user_xml = used_user_xml.replace('THUMBPRINT', thumbprint)
        used_xml = used_xml.replace('PROFILE', profilename)
        used_xml = used_xml.replace('<name>SSID</name>', '<name>%s</name>'%ssid)
        used_xml = used_xml.strip()
        used_user_xml = used_user_xml.strip()

        ascii_used_xml = ''.join(['\\\\%o'%(ord(x)) for x in used_xml])
        
        self.cmd('printf "%s" > "%s"' % (ascii_used_xml, join(dest_path, xml_file_name)), timeout=120)
        self.cmd('cat "%s"' % join(dest_path, xml_file_name))

        if used_user_xml:
            ascii_used_user_xml = ''.join(['\\\\%o'%(ord(x)) for x in used_user_xml])
            self.cmd('printf "%s" > "%s"' % (ascii_used_user_xml, join(dest_path, user_xml_file_name)), timeout=120)
            self.cmd('cat "%s"' % join(dest_path, user_xml_file_name))

    def del_xml_file(self, profilename, dest='c:/client'):
        xml_file_name = '%s.xml' % profilename
        user_xml_file_name = 'user_%s.xml' % profilename
        self.cmd('rm -rf %s' % join(dest, xml_file_name))
        self.cmd('rm -rf %s' % join(dest, user_xml_file_name))

    def client_do_connect(self, **kwargs):
        interface = kwargs.get('interface', 'Wireless Network Connection')
        ssid = kwargs.get('ssid')
        if not ssid:
            raise ExceptionWin('You must provide ssid parameter for this function')
        profilename = kwargs.get('profilename', ssid)
        bssid = kwargs.get('bssid', '000000000000')
        bssid = bssid.replace(':', '')
        eap = kwargs.get('eap')
        path = kwargs.get('path', 'c:/client') # The path of the tool client.exe
        client_exe = join(path, 'client.exe')
        xml_file = join(path, '%s.xml'%profilename)

        if eap:
            user_xml_file = join(path, 'user_%s.xml'%profilename)
            command = '%s conn "%s" "%s" %s %s %s' % (client_exe, ssid, profilename ,xml_file, bssid, user_xml_file)
        else:
            command = '%s conn "%s" "%s" %s %s' % (client_exe, ssid, profilename, xml_file, bssid)

        ret = self.cmd(command)
        if 'completed successfully' in ret:
            return True
        else:
            return False

    def connect_wifi(self, **kwargs):
        '''
        Combine gen_xml_file and client_do_connect
        '''
        self.gen_xml_file(**kwargs)
        return self.client_do_connect(**kwargs)

    def is_wifi_connected(self, path='c:/client'):
        client_exe = join(path, 'client.exe')
        ret = self.cmd("%s gs" % client_exe)
        if '"connected"' in ret:
            return True
        else:
            return False
