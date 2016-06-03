'''
TestCategory: Authentication
TestCase: RT-1789 Support different format calling-station-id and called-station-id

Requirement:
    1. ssid-profile configuration in cli
        wlan ssid-profile <ssid-profile-name>
            use-ip-for-calling-station
            no use-ip-for-calling-station

            called-station-id type {ap-group | ap-mac | ap-name | ipaddr | macaddr | vlan-id} // default: macaddr
            no called-station-id type

            called-station-id include-ssid [delimiter <delimiter>]
            no called-station-id include-ssid

    2. Should work for auth and acct
        should work on dot1x, mac, cp

    3. if no valid ip for client, force to macaddr

    4. vlan-id should be client vlan
        bridge is vlan 1 ??
        magic vlan is 3333 ???

    5. Keep current mac-authentication and auth-pkt-mac-format logical

    6. do not impact aaa test-server

    7. do we need to add to wired profile ??

    8. if called-station-id type is default, do we need to show it in cli ??

    9. called-station-id ,what do we define macaddr and ap-mac ??

    10. do we need to handle ipv6 ??

Mind Map:
                                                                                                    |--- use-ip-for-calling-station / no use-ip-for-calling-station
                                                                                                    |--- called-station-id type <STRING:csid_type:Calling_Station_ID_Type> / no ...
                                                                                                    |--- called-station-id include-ssid { delimiter <STRING:delim:Delimiter> } / no ...
                                                                                                    |  |--- help: use-ip-for-calling-station
                                                                                                    |  |--- help: called-station-id
                                                                    |---- cparser --> ap-wlan.cli ---  |        |--- boolean wl_use_ip_for_calling_station
                                                                    |---- cli_help.c -------------------        |--- ?? <authcmnserver.h> rad_called_station_id wl_called_station_id or boolean/__u8/__8 called_station_id_t
                                                                    |---- cli_config.h --> wlan_ssid_profile_t --   |--- Implement: cparser_cmd_wlan_profile_use_ip_for_calling_station
                                                                    |---- cli_wlan.c ----------------------------------- Implement: cparser_cmd_wlan_profile_no_use_ip_for_calling_station
                                                                    |                                               |--- Implement: cparser_cmd_wlan_profile_called_station_id_type_csid_type
                                                                    |                                               |--- Implement: cparser_cmd_wlan_profile_no_called_station_id_type
                                                                    |                                               |--- Implement: cparser_cmd_wlan_profile_called_station_id_include_ssid_delimiter_delim
                                                                   cli                                              |--- Implement: cparser_cmd_wlan_profile_no_called_station_id_include_ssid
                                                                    |                                               |--- Implement: cparser_cmd_wlan_profile_no_called_station_id
                                                                    |                                               |--- add them to send_ssid_configuration_message
                                                                    |                                               |--- add them into cli_wlan_saved
                                                                    |---- cli_swarm.c --------------- add them into recv_show_swarm_network
                                                    RT-1789 |--------
                                                                    |    |-- wifi_mgmt.h -- _ssid_config_info -- use_ip_for_calling_station
                                                                    |    |                                    |- called_station_id_type 
                                                                    |    |                                    |- called_station_id_include_ssid
                                                                    |    |                                    |- called_station_id_delimiter
                                                                   stm - |
                                                                    |    |-- stm_intf.c -- handle_ssid_configuration_message
                                                                    |    |
                                                                    |    |-- radhdlr.c -- create_vps_explict
                                                                   auth
                                                                    |------ rc_aal.c --- definition - iap_fmt_called_station_id
                                                                    |------ rc_api.c --- set_common_attr
                                                                    |------ rc_acct_instant.c --- rc_acct_common_vplist
'''
from tests import *

IAP1, IAP2, IAP3, CLIENT1, CLIENT2, RADIUS = REQUIRED('IAP1', 'IAP2', 'IAP3', 'CLIENT1', 'CLIENT2', 'RADIUS')

iap1 = IAP('IAP1', IAP1['MGT-METHOD'], host=IAP1['MGT-IP'], port=IAP1['MGT-PORT'], username=IAP1['USERNAME'], password=IAP1['PASSWORD'], console=True)
iap2 = IAP('IAP2', IAP2['MGT-METHOD'], host=IAP2['MGT-IP'], port=IAP2['MGT-PORT'], username=IAP2['USERNAME'], password=IAP2['PASSWORD'], console=True)
iap3 = IAP('IAP3', IAP3['MGT-METHOD'], host=IAP3['MGT-IP'], port=IAP3['MGT-PORT'], username=IAP3['USERNAME'], password=IAP3['PASSWORD'], console=True)

client1 = Win('CLIENT1', CLIENT1['MGT-METHOD'], host=CLIENT1['MGT-IP'], username=CLIENT1['USERNAME'], password=CLIENT1['PASSWORD'], timeout=60)
client2 = Win('CLIENT2', CLIENT2['MGT-METHOD'], host=CLIENT2['MGT-IP'], username=CLIENT2['USERNAME'], password=CLIENT2['PASSWORD'], timeout=60)

radius = Linux('RADIUS', RADIUS['MGT-METHOD'], host=RADIUS['MGT-IP'], username=RADIUS['USERNAME'], password=RADIUS['PASSWORD'], timeout=60)

master = None
slave = None

auth_server_name = 'fd1'
auth_server = IAP.get_conf_auth_server(auth_server_name, **{'ip':'10.65.10.59', 'port':'1812',
                                                            'acctport':'1813', 'key':'testing123'})
csid_types = ['macaddr', 'ipaddr', 'ap-macaddr', 'ap-group', 'ap-name', 'vlan-id']

username, password = 'fengding', 'fengding'

ssid_1x, ssid_cp, ssid_mac = 'iutf-1x', 'iutf-cp', 'iutf-mac'
ssid_configuration = {}
no_ssid_configuration = {}
ssid_configuration[ssid_1x] = IAP.get_conf_ssid(ssid_1x, 'auth-pkt-mac-format upper-case delimiter -',
                                **{'opmode':'wpa2-aes', 'auth-server':auth_server_name})
no_ssid_configuration[ssid_1x] = 'no wlan ssid-profile "%s"' % ssid_1x
ssid_configuration[ssid_cp] = IAP.get_conf_ssid(ssid_cp, 'auth-pkt-mac-format upper-case delimiter -',
                                **{'opmode':'opensystem', 'auth-server':auth_server_name, 'captive-portal': 'captive-portal',
                                   'type':'guest', 'vlan':'guest'})
no_ssid_configuration[ssid_cp] = 'no wlan ssid-profile "%s"' % ssid_cp
ssid_configuration[ssid_mac] = IAP.get_conf_ssid(ssid_mac, 'mac-authentication-upper-case', 'mac-authentication',
                                **{'opmode':'opensystem', 'auth-server':auth_server_name, 'mac-authentication-delimiter': '-',
                                   'type':'employee'})
no_ssid_configuration[ssid_mac] = 'no wlan ssid-profile "%s"' % ssid_mac

def setup_module():
    '''
    setup for this test script, will be executed before all testcases in the script.
    '''
    global master, slave
    assert iap1.connect()
    assert iap2.connect()
    assert iap3.connect()
    assert client1.connect()
    assert client2.connect()
    assert radius.connect()
    master = IAP.get_master(iap1, iap2, iap3)
    assert master is not None, "We did not find master in the cluster or found more than one master"
    slaves = [iap for iap in [iap1, iap2, iap3] if iap != master]
    slave = choice(slaves)

    log.info('Configure auth server and SSID in setup')
    master.cfg(auth_server)
    master.cfg(ssid_configuration[ssid_1x])
    master.cfg(ssid_configuration[ssid_cp])
    master.cfg(ssid_configuration[ssid_mac])

def teardown_module():
    '''
    teardown fro the test script, will be executed after all testcases in the script.
    '''
    master2 = IAP.get_master(iap1, iap2, iap3)
    master2.cfg('no wlan auth-server "%s"' % auth_server_name)
    master2.cfg(no_ssid_configuration[ssid_1x])
    master2.cfg(no_ssid_configuration[ssid_cp])
    master2.cfg(no_ssid_configuration[ssid_mac])
    assert master == master2, 'Master failover during testing, please check'
    iap1.disconnect()
    iap2.disconnect()
    iap3.disconnect()
@nottest
def configure_use_ip_for_calling_station(ssid):
    master.cfg(IAP.get_conf_ssid(ssid, True, 'use-ip-for-calling-station'))
    sleep(10)
    ret = master.cmd('show running')
    assert 'use-ip-for-calling-station' in ret, 'use-ip-for-calling-station is not in configuration'
    ret = master.cmd('show network %s'%ssid)
    assert 'Use IP for Calling-Station-ID :Enabled' in ret, 'use-ip-for-calling-station is not enabled in show network'

@nottest
def configure_no_use_ip_for_calling_station(ssid):
    master.cfg(IAP.get_conf_ssid(ssid, True, 'no use-ip-for-calling-station'))
    sleep(10)
    ret = master.cmd('show running')
    assert 'use-ip-for-calling-station' not in ret, 'use-ip-for-calling-station is not deleted'
    ret = master.cmd('show network %s'%ssid)
    assert 'Use IP for Calling-Station-ID :Disabled' in ret, 'use-ip-for-calling-station is not disabled in show network'

@nottest
def configure_called_station_id_type(ssid, csid_type):
    master.cfg(IAP.get_conf_ssid(ssid, True, 'called-station-id type %s'%csid_type))
    sleep(10)
    ret = master.cmd('show network %s'%ssid)
    if csid_type not in csid_types:
        csid_type = csid_types[0]
    assert 'Called-Station-ID Type :%s'%csid_type in ret

@nottest
def configure_no_called_station_id_type(ssid):
    master.cfg(IAP.get_conf_ssid(ssid, True, 'no called-station-id type'))
    sleep(10)
    ret = master.cmd('show network %s'%ssid)
    assert 'Called-Station-ID Type :macaddr' in ret

@nottest
def configure_called_station_id_include_ssid(ssid, delimiter=None):
    if delimiter and len(delimiter)==1:
        master.cfg(IAP.get_conf_ssid(ssid, True, 'called-station-id include-ssid delimiter %s'%delimiter))
    else:
        master.cfg(IAP.get_conf_ssid(ssid, True, 'called-station-id include-ssid'))
    sleep(10)
    ret = master.cmd('show network %s'%ssid)
    assert 'Called-Station-ID Include SSID :Enabled' in ret
    if delimiter and len(delimiter)==1:
        assert 'Called-Station-ID Include SSID Delimiter :%s'%delimiter in ret

@nottest
def configure_no_called_station_id_include_ssid(ssid):
    master.cfg(IAP.get_conf_ssid(ssid, True, 'no called-station-id include-ssid'))
    sleep(10)
    ret = master.cmd('show network %s'%ssid)
    assert 'Called-Station-ID Include SSID :Disabled' in ret

@nottest
def configure_no_called_station_id(ssid):
    master.cfg(IAP.get_conf_ssid(ssid, True, 'no called-station-id'))
    sleep(10)
    ret = master.cmd('show network %s'%ssid)
    assert 'Called-Station-ID Include SSID :Disabled' in ret
    assert 'Called-Station-ID Type :macaddr' in ret

def test_verify_configuration_use_ip_for_calling_station():
    '''
    Test use-ip-for-calling-station in show running
    Use IP for Calling-Station-ID: Enabled in show network
    '''
    configure_use_ip_for_calling_station(ssid_1x)

def test_verify_configuration_no_use_ip_for_calling_station():
    '''
    Test no use-ip-for-calling-station
    This shoud be valid to remove the configuration use-ip-for-calling-station.
    '''
    configure_no_use_ip_for_calling_station(ssid_1x)

def test_verify_configuration_called_station_id_type_macaddr_as_default():
    '''
    Test called-station-id type macaddr, the default value should be macaddr
    '''
    configure_called_station_id_type(ssid_1x, 'macaddr')
    configure_no_called_station_id_type(ssid_1x)

def test_verify_configuration_called_station_id_type_ipaddr():
    '''
    Test called-station-id type ipaddr
    '''
    configure_called_station_id_type(ssid_1x, 'ipaddr')

def test_verify_configuration_no_called_station_id_type():
    '''
    Test no called-station-id type
    '''
    configure_no_called_station_id_type(ssid_1x)

# def test_verify_configuration_called_station_id_type_ap_addr():
#     '''
#     Test called-station-id type ap-macaddr
#     '''
#     master.cfg(IAP.get_conf_ssid(ssid_1x_mac, edit=True, 'called-station-id type ap-macaddr'))
#     sleep(10)
#     ret = master.cmd('show network %s'%ssid_1x_mac)
#     assert 'Called-Station-ID Type :ap-macaddr' in ret

def test_verify_configuration_called_station_id_type_ap_group():
    '''
    Test called-station-id type ap-group
    '''
    configure_called_station_id_type(ssid_1x, 'ap-group')

def test_verify_configuration_called_station_id_type_ap_name():
    '''
    Test called-station-id type ap-name
    '''
    configure_called_station_id_type(ssid_1x, 'ap-name')

def test_verify_configuration_called_station_id_type_vlan_id():
    '''
    Test called-station-id type vlan-id
    '''
    configure_called_station_id_type(ssid_1x, 'vlan-id')

def test_verify_configuration_called_station_id_include_ssid():
    '''
    Test called-station-id include-ssid
    '''
    configure_called_station_id_include_ssid(ssid_1x)

def test_verify_configuration_called_station_id_include_ssid_delimiter():
    '''
    Test called-station-id include-ssid
    '''
    configure_called_station_id_include_ssid(ssid_1x, '-')

def test_verify_configuration_no_called_station_id_include_ssid():
    '''
    Test called-station-id include-ssid
    '''
    configure_no_called_station_id_include_ssid(ssid_1x)

def test_verify_configuration_no_called_station_id():
    '''
    Test no called-station-id
    '''
    configure_called_station_id_type(ssid_1x, 'vlan-id')
    configure_called_station_id_include_ssid(ssid_1x, '-')
    configure_no_called_station_id(ssid_1x)

def test_verify_function_use_ip_for_calling_station_in_1x():
    '''
    Test use-ip-for-calling-station can work properly in 802.1x authentication
    '''
    configure_use_ip_for_calling_station(ssid_1x)


def test_verify_function_no_use_ip_for_calling_station_in_1x():
    pass

def test_verify_function_use_ip_for_calling_station_in_cp():
    pass

def test_verify_function_no_use_ip_for_calling_station_in_cp():
    pass

def test_verify_function_use_ip_for_calling_station_in_mac():
    pass

def test_verify_function_no_use_ip_for_calling_station_in_mac():
    pass

def test_verify_function_called_station_id_type_macaddr_in_mac_1x():
    pass

def test_verify_function_called_station_id_type_macaddr_in_cp_mac():
    pass

def test_verify_function_called_station_id_type_ipaddr_in_mac_1x():
    pass

def test_verify_function_called_station_id_type_ipaddr_in_cp_mac():
    pass

def test_verify_function_called_station_id_type_ap_macaddr_in_mac_1x():
    pass

def test_verify_function_called_station_id_type_ap_macaddr_in_cp_mac():
    pass

def test_verify_function_called_station_id_type_ap_group_in_mac_1x():
    pass

def test_verify_function_called_station_id_type_ap_group_in_cp_mac():
    pass

def test_verify_function_called_station_id_type_ap_name_in_mac_1x():
    pass

def test_verify_function_called_station_id_type_ap_name_in_cp_mac():
    pass

def test_verify_function_called_station_id_type_vlan_id_in_mac_1x():
    pass

def test_verify_function_called_station_id_type_vlan_id_in_cp_mac():
    pass

def test_verify_function_no_called_station_id_type_in_mac_1x():
    pass

def test_verify_function_no_called_station_id_type_in_cp_mac():
    pass

def test_verify_function_called_station_id_include_ssid_in_mac_1x():
    pass

def test_verify_function_called_station_id_include_ssid_in_cp_mac():
    pass

def test_verify_function_called_station_id_include_ssid_delimiter_in_mac_1x():
    pass

def test_verify_function_called_station_id_include_ssid_delimiter_in_cp_mac():
    pass

def test_verify_function_no_called_station_id_include_ssid_in_mac_1x():
    pass

def test_verify_function_no_called_station_id_include_ssid_in_cp_mac():
    pass

def test_verify_function_no_called_station_id_in_mac_1x():
    pass

def test_verify_function_no_called_station_id_in_cp_mac():
    pass
