'''
TestCategory: Authentication
TestCase: Captive Portal statemachine Testing
State Machine:
                                        Client visits a url
                                                |
                                 YES ----- URL is FQDN ?------ No
                                  |                             |
                        Client sends DNS request                |
                                  |                             |
                     NO ---- DNS resolved ? --- Yes ------ is scheme http --- No --- Hitting acl "any any 6 0-65535 443-443 PSD4"
                     |                                           |                                          |
                Splash page failed                              YES                          DNAT: x.x.x.x:443 -> 172.31.98.1:4343
                                                                 |                           SNAT: y.y.y.y     -> 172.31.98.2
                                            Hitting acl "any any 6 0-65535 80 80 PSD4"                      |
                                                                 |                           minihttpd will handle it and reply back a http redirect to client
                                            DNAT: x.x.x.x:80 -> 172.31.98.1:8080
                                            SNAT: y.y.y.y    -> 172.31.98.2
                                                                 |
                                 tiny proxy will handle it and reply back a http redirect to client
                                                                 |
                                           ICP ---------------------------------------- ECP
                                            |                                            |
                                Splash page in Client                           Splash page in Client ------------- Pop up ECP page in Client
                                            |                                                                                   |
              YES ------------- Has Installed certificate?                                            Client post username and password to the url for IAP
               |                            |                                                                                   |
               |                            NO                                                                            Has Installed cert ? ---------------- No
               |                            |                                                                                   |                               |
               |        URL: https://securelogin.arubanetworks.com/swarm.cgi?...                                               Yes             URL: https://securelogin.arubanetworks.com/cgi-bin/login
               |                                              |                                                                 |                               |
    URL: https://<cn for the CP cert>/swarm.cgi?...           |                                          URL: https://<cn for the CP cert>/cgi-bin/login        |
               |                                              |                                                                 |                               |
               ------------------------------------------------                                                                 ---------------------------------
                                    |                                                                                                       |
  Pop up --------- No -------- Is this url resolved to 172.31.98.1 in client ? --------------------------------------------------------------
 portal page failed                 |
                                   Yes
                                    |
                        Pop up internal portal page
                                    |
                client post username and password to 172.31.98.1
                                    |
            IAP check the username and password from radius server by PAP (Internal server should be the inner DB)

Test Topology:
               -------------------------------------- Manager Switch -------------------------
               |           |             |                    |                               |
               |           |          Radius ------------ Tester Switch --------------        |
               |           |                      |          |           |                Console server
               |           |                     IAP1       IAP1        IAP1 ******************    *  *
               |           |                      *          ***************************************  *
               |           |                      *****************************************************
            Win 7         Win 7
            Laptop        Laptop
    - : Eth connection 
    * : Console connection

TestSteps:
    test_internalCaptivePortalAck:
        1 > Create 1 ssid from Master IAP (With internal captive portal)
          * The ssid configuration should be push sucessfully in both Master and Slaves
        2 > Make the two laptops connect to Master and one of Slaves respectively 
            Assume Client1 connect to Master
            Assume Client2 connect to Slave
          * Should connect sucessfully
        3 > Use wget to visit one http url in Client, here, we use "http://www.baidu.com"
            "wget --secure-protocal=TLSv1 --no-check-certificate -t 1 -o debug.log -O output.html http://www.baidu.com"
          * The captive portal html code should be found in output.html
        4 > Use wget to post auth request to securelogin.arubanetworks.com
            "wget --secure-protocal=TLSv1 --no-check-certificate -t 1 -o debug.log -O output.html \
            --post-data 'orig_url=http://www.baidu.com&opcode=cp_ack&instant@arubanetworks.com' \
            'https://securelogin.arubanetworks.com/swarm.cgi'"
          * Client should be able to past auth and a redirect to baidu html code should be found in output.html
        5 > Check the acl for this client
          * this acl should be permit all
        6 > ping from client to baidu.com
          * ping should pass
'''

from tests import *

IAP1, IAP2, IAP3, CLIENT1, CLIENT2 = REQUIRED('IAP1', 'IAP2', 'IAP3', 'CLIENT1', 'CLIENT2')

iap1 = IAP('IAP1', IAP1['MGT-METHOD'], host=IAP1['MGT-IP'], port=IAP1['MGT-PORT'], username=IAP1['USERNAME'], password=IAP1['PASSWORD'], console=True)
iap2 = IAP('IAP2', IAP2['MGT-METHOD'], host=IAP2['MGT-IP'], port=IAP2['MGT-PORT'], username=IAP2['USERNAME'], password=IAP2['PASSWORD'], console=True)
iap3 = IAP('IAP3', IAP3['MGT-METHOD'], host=IAP3['MGT-IP'], port=IAP3['MGT-PORT'], username=IAP3['USERNAME'], password=IAP3['PASSWORD'], console=True)

client1 = Win('CLIENT1', CLIENT1['MGT-METHOD'], host=CLIENT1['MGT-IP'], username=CLIENT1['USERNAME'], password=CLIENT1['PASSWORD'], timeout=60)
client2 = Win('CLIENT2', CLIENT2['MGT-METHOD'], host=CLIENT2['MGT-IP'], username=CLIENT2['USERNAME'], password=CLIENT2['PASSWORD'], timeout=60)
master = None
slave = None

ssid = 'iutf-cp'
ssid_configuration = IAP.get_conf_ssid(ssid, **{'opmode':'wpa2-psk-aes', 'wpa-passphrase':'12345678',
                                                     'vlan':'guest', 'auth-server':'InternalServer',
                                                     'captive-portal':'internal'})
no_ssid_configuration = 'no wlan ssid-profile "%s"' % ssid

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
    master = IAP.get_master(iap1, iap2, iap3)
    assert master is not None, "We did not find master in the cluster or found more than one master"
    slaves = [iap for iap in [iap1, iap2, iap3] if iap != master]
    slave = choice(slaves)

def teardown_module():
    '''
    teardown fro the test script, will be executed after all testcases in the script.
    '''
    iap1.disconnect()
    iap2.disconnect()
    iap3.disconnect()

def setup_internalCaptivePortalAck():
    log.info('setup for test case internalCaptivePortalAck')

def teardown_internalCaptivePortalAck():
    log.info('teardown for test case internalCaptivePortalAck')
    master.cfg(no_ssid_configuration)
    client1.del_xml_file(ssid)
    client2.del_xml_file(ssid)

@with_setup(setup_internalCaptivePortalAck, teardown_internalCaptivePortalAck)
def test_internalCaptivePortalAck():
    '''
    Test script for testing internalCaptivePortalAck
    '''
    log.info('1. Create ssid from Master')
    master.cfg(ssid_configuration)
    log.info('1. a. Waiting 10 seconds here')
    sleep(10)
    for iap in [iap1, iap2, iap3]:
        ret = iap.cmd('show network')
        ret_dict = iap.show_table_parser(ret)
        ssidlist = ret_dict['Networks'].get('Key') or ret_dict['Networks'].get('ESSID')
        assert ssidlist, 'ssid list should not be None, please check script or the latest show network format'
        assert 'iutf-cp' in ssidlist, 'the ssid was not pushed to %s'%iap.device_name

    log.info("2. Make the two laptops connect to Master and one of Slaves respectively")

    log.info("2. a. Get band a bssid from Master")
    master_bssid = master.get_bssid(ssid, 'a')
    assert master_bssid, 'Got Master bssid failed'
    log.info("2. b. Make client1 connect to Master")
    client1.connect_wifi(ssid=ssid, authentication='wpa2-psk', password='12345678', bssid=master_bssid)
    sleep(10)
    if not client1.is_wifi_connected():
        log.info("Try again...")
        client1.client_do_connect(ssid=ssid, bssid=master_bssid)
        sleep(10)
        assert client1.is_wifi_connected(), 'Client1 connected to Master failed'

    log.info("2. c. Get band a bssid from Slave")
    slave_bssid = slave.get_bssid(ssid, 'a')
    assert slave_bssid, 'Got Slave bssid failed'
    log.info("2. d. Make client2 connect to Slave")
    client2.connect_wifi(ssid=ssid, authentication='wpa2-psk', password='12345678', bssid=slave_bssid)
    sleep(10)
    if not client2.is_wifi_connected():
        log.info("Try again...")
        client2.client_do_connect(ssid=ssid, bssid=slave_bssid)
        sleep(10)
        assert client2.is_wifi_connected(), 'Client2 connected to Slave failed'

    log.info("3. a. visit url in Client1 which connected to Master")
    client1.cmd("wget --secure-protocal=TLSv1 --no-check-certificate -t 1 -o debug.log -O output.html http://www.baidu.com")
    ret = client1.cmd("cat ./output.html")



