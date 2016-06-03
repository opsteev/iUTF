#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import os
from ilog import log, Ilogger

_TESTBED = 'iap_225'
_TESTBED_DIR = "./testbeds"

global TESTBED

TESTBED = {}

class ExceptionTestbed(Exception):
    '''Raised for Testbed exceptions.
    '''

if '--testbed-dir' in sys.argv:
    _TESTBED_DIR = sys.argv[sys.argv.index('--testbed-dir')+1]

if '--testbed' in sys.argv:
    _TESTBED = sys.argv[sys.argv.index('--testbed')+1]

testbed_file = os.path.join(_TESTBED_DIR, _TESTBED)
try:
    fd = open(testbed_file, 'r')
    testbed_ctx = fd.read()
    log.debug("Testbed content: %r" % testbed_ctx)
    TESTBED = json.loads(testbed_ctx)
    log.debug("decoded json: %r" % TESTBED)
except:
    log.error("Load testbed %s failed" % testbed_file)
finally:
    fd.close()

def REQUIRED(*duts):
    global TESTBED
    for dut in duts:
        if dut not in TESTBED['DUT']:
            log.error("testbed does not have enough devices for the script.")
            log.debug(TESTBED)
            raise ExceptionTestbed('Incorrect testbed - script mapping.')
    
    return [TESTBED[dut] for dut in duts]