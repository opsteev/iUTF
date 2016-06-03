#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import os
import argparse
from ilog import log, Ilogger

_TESTBED = 'iap_225'
_TESTBED_DIR = "./testbeds"

global TESTBED

TESTBED = {}

class ExceptionTestbed(Exception):
    '''Raised for Testbed exceptions.
    '''

parser = argparse.ArgumentParser()
parser.add_argument("--testbed")
parser.add_argument("--testbed-dir")
args, unknown = parser.parse_known_args()
log.debug("testbed: %s" % args.testbed)
log.debug("testbed_dir: %s" % args.testbed_dir)

if args.testbed_dir:
    _TESTBED_DIR = arg.testbed_dir

if args.testbed:
    _TESTBED = args.testbed

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
