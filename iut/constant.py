'''
Define global variable in this file for iutf.
'''

WIN_WIRELESS_XML = {}
WIN_WIRELESS_XML['OPEN'] = '''
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>PROFILE</name>
    <SSIDConfig>
        <SSID>
            <name>SSID</name>
        </SSID>
        <nonBroadcast>false</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>open</authentication>
                <encryption>none</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
        </security>
    </MSM>
</WLANProfile>
'''

WIN_WIRELESS_XML['WEP-STATIC'] = '''
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>PROFILE</name>
    <SSIDConfig>
        <SSID>
            <name>SSID</name>
        </SSID>
        <nonBroadcast>false</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>open</authentication>
                <encryption>WEP</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>networkKey</keyType>
                <protected>false</protected>
                <keyMaterial>WEP_KEY</keyMaterial>
            </sharedKey>
            <keyIndex>WEPKEY_INDEX</keyIndex>
        </security>
    </MSM>
</WLANProfile>
'''

WIN_WIRELESS_XML['WPA-PSK'] = '''
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>PROFILE</name>
    <SSIDConfig>
        <SSID>
            <name>SSID</name>
        </SSID>
        <nonBroadcast>false</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPAPSK</authentication>
                <encryption>TKIP</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>WPA_PSK</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
'''

WIN_WIRELESS_XML['WPA2-PSK'] = '''
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>PROFILE</name>
    <SSIDConfig>
        <SSID>
            <name>SSID</name>
        </SSID>
        <nonBroadcast>false</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>WPA2_PSK</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
'''

WIN_WIRELESS_XML['PEAP-GTC'] = '''
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>PROFILE</name>
    <SSIDConfig>
        <SSID>
            <name>SSID</name>
        </SSID>
        <nonBroadcast>false</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>AUTHENTICATION</authentication>
                <encryption>ENCRYPTION</encryption>
                <useOneX>true</useOneX>
            </authEncryption>
            <OneX xmlns="http://www.microsoft.com/networking/OneX/v1">
                <authMode>machineOrUser</authMode>
                <EAPConfig>
                    <EapHostConfig xmlns="http://www.microsoft.com/provisioning/EapHostConfig">
                        <EapMethod>
                            <Type xmlns="http://www.microsoft.com/provisioning/EapCommon">25</Type>
                            <VendorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorId>
                            <VendorType xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorType>
                            <AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">9</AuthorId>
                        </EapMethod>
                        <Config xmlns="http://www.microsoft.com/provisioning/EapHostConfig">
                            <eapPeap xmlns="http://www.cisco.com/CCX">
                                <doNotValidateServerCertificate/>
                                <unprotectedIdentityPattern encryptContent="false">AUTOMATION</unprotectedIdentityPattern>
                                <enableFastReconnect><alwaysAttempt/></enableFastReconnect>
                                <authMethods>
                                    <builtinMethods>
                                        <authenticateWithPassword>
                                            <protectedIdentityPattern encryptContent="false">USERNAME</protectedIdentityPattern>
                                            <passwordSource>
                                                <passwordFromProfile encryptContent="false">PASSWORD</passwordFromProfile>
                                            </passwordSource>
                                            <methods>
                                                <eapGtc/>
                                            </methods>
                                        </authenticateWithPassword>
                                    </builtinMethods>
                                </authMethods>
                            </eapPeap>
                        </Config>
                    </EapHostConfig>
                </EAPConfig>
            </OneX>
        </security>
    </MSM>
</WLANProfile>
'''

WIN_WIRELESS_XML['PEAP-MSCHAPV2'] = '''
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>PROFILE</name>
    <SSIDConfig>
        <SSID>
            <name>SSID</name>
        </SSID>
        <nonBroadcast>false</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>AUTHENTICATION</authentication>
                <encryption>ENCRYPTION</encryption>
                <useOneX>true</useOneX>
            </authEncryption>
            <OneX xmlns="http://www.microsoft.com/networking/OneX/v1">
                <cacheUserData>true</cacheUserData>
                <authMode>user</authMode>
                <EAPConfig>
                    <EapHostConfig xmlns="http://www.microsoft.com/provisioning/EapHostConfig">
                        <EapMethod>
                            <Type xmlns="http://www.microsoft.com/provisioning/EapCommon">25</Type>
                            <VendorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorId>
                            <VendorType xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorType>
                            <AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</AuthorId>
                        </EapMethod>
                        <Config xmlns="http://www.microsoft.com/provisioning/EapHostConfig">
                            <Eap xmlns="http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1">
                                <Type>25</Type>
                                <EapType xmlns="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV1">
                                    <ServerValidation>
                                        <DisableUserPromptForServerValidation>false</DisableUserPromptForServerValidation>
                                        <ServerNames></ServerNames>
                                    </ServerValidation>
                                    <FastReconnect>true</FastReconnect>
                                    <InnerEapOptional>false</InnerEapOptional>
                                    <Eap xmlns="http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1">
                                        <Type>26</Type>
                                        <EapType xmlns="http://www.microsoft.com/provisioning/MsChapV2ConnectionPropertiesV1">
                                            <UseWinLogonCredentials>false</UseWinLogonCredentials>
                                        </EapType>
                                    </Eap>
                                    <EnableQuarantineChecks>false</EnableQuarantineChecks>
                                    <RequireCryptoBinding>false</RequireCryptoBinding>
                                    <PeapExtensions>
                                        <PerformServerValidation xmlns="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV2">false</PerformServerValidation>
                                        <AcceptServerName xmlns="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV2">false</AcceptServerName>
                                    </PeapExtensions>
                                </EapType>
                            </Eap>
                        </Config>
                    </EapHostConfig>
                </EAPConfig>
            </OneX>
        </security>
    </MSM>
</WLANProfile>
'''

WIN_WIRELESS_XML['MSCHAPV2-USER'] = '''
<?xml version="1.0"?>
<EapHostUserCredentials xmlns="http://www.microsoft.com/provisioning/EapHostUserCredentials" xmlns:eapCommon="http://www.microsoft.com/provisioning/EapCommon" xmlns:baseEap="http://www.microsoft.com/provisioning/BaseEapMethodUserCredentials">
    <EapMethod>
        <Type xmlns="http://www.microsoft.com/provisioning/EapCommon">25</Type>
        <VendorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorId>
        <VendorType xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorType>
        <AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</AuthorId>
    </EapMethod>
    <Credentials>
        <Eap xmlns="http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1">
            <Type xmlns="http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1">25</Type>
            <EapType xmlns="http://www.microsoft.com/provisioning/MsPeapUserPropertiesV1">
                <Eap xmlns="http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1">
                    <Type xmlns="http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1">26</Type>
                    <EapType xmlns="http://www.microsoft.com/provisioning/MsChapV2UserPropertiesV1">
                        <Username xmlns="http://www.microsoft.com/provisioning/MsChapV2UserPropertiesV1">USERNAME</Username>
                        <Password xmlns="http://www.microsoft.com/provisioning/MsChapV2UserPropertiesV1">PASSWORD</Password>
                    </EapType>
                </Eap>
            </EapType>
        </Eap>
    </Credentials>
</EapHostUserCredentials>
'''

WIN_WIRELESS_XML['TLS'] = '''
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>PROFILE</name>
    <SSIDConfig>
        <SSID>
        <name>SSID</name>
        </SSID>
        <nonBroadcast>false</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>AUTHENTICATION</authentication>
                <encryption>ENCRYPTION</encryption>
                <useOneX>true</useOneX>
            </authEncryption>
            <OneX xmlns="http://www.microsoft.com/networking/OneX/v1">
                <authMode>user</authMode>
                <EAPConfig>
                    <EapHostConfig xmlns="http://www.microsoft.com/provisioning/EapHostConfig">
                        <EapMethod>
                            <Type xmlns="http://www.microsoft.com/provisioning/EapCommon">13</Type>
                            <VendorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorId>
                            <VendorType xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorType>
                            <AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</AuthorId>
                        </EapMethod>
                        <Config>
                            <Eap xmlns="http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1">
                                <Type>13</Type>
                                <EapType xmlns="http://www.microsoft.com/provisioning/EapTlsConnectionPropertiesV1">
                                    <CredentialsSource>
                                        <CertificateStore/>
                                    </CredentialsSource>
                                    <DifferentUsername>true</DifferentUsername>
                                </EapType>
                            </Eap>
                        </Config>
                    </EapHostConfig>
                </EAPConfig>
            </OneX>
        </security>
    </MSM>
</WLANProfile>
'''

WIN_WIRELESS_XML['TLS-CERT'] = '''
<?xml version="1.0"?>
<EapHostUserCredentials xmlns="http://www.microsoft.com/provisioning/EapHostUserCredentials" xmlns:eapCommon="http://www.microsoft.com/provisioning/EapCommon" xmlns:baseEap="http://www.microsoft.com/provisioning/BaseEapMethodUserCredentials">
    <EapMethod>
        <Type xmlns="http://www.microsoft.com/provisioning/EapCommon">13</Type>
        <AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</AuthorId>
   </EapMethod>
   <Credentials>
        <Eap xmlns="http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1">
            <Type xmlns="http://www.microsoft.com/provisioning/BaseEapUserPropertiesV1">13</Type> 
            <EapType xmlns="http://www.microsoft.com/provisioning/EapTlsUserPropertiesV1">
                <Username xmlns="http://www.microsoft.com/provisioning/EapTlsUserPropertiesV1">CERTNAME</Username> 
                <UserCert xmlns="http://www.microsoft.com/provisioning/EapTlsUserPropertiesV1">THUMBPRINT</UserCert> 
            </EapType>
        </Eap>
   </Credentials>
</EapHostUserCredentials>
'''

