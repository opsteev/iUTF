#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import nose
import json
from nose.plugins import Plugin

class Testbed(Plugin):
    name = 'testbed'

    def __init__(self, verbosity=1):
        super(Testbed, self).__init__()
        self.verbosity = verbosity

    def options(self, parser, env=os.environ):
        super(Testbed, self).options(parser, env=env)
        parser.add_option(
            '--testbed', action='store',
            dest='testbed', metavar="FILE",
            default=env.get('NOSE_TESTBED_FILE', "testbed1"),
            help="Path to testbed json file to get the json parameter to all tests. "
                 "Default is testbed1 in the working directory "
                 "[NOSE_TESTBED_FILE]")
        parser.add_option(
            '--testbed-dir', action='store',
            dest='testbed_dir', metavar="WHERE",
            default=env.get('NOSE_TESTBED_DIR', "./testbeds"),
            help="The folder of testbeds. "
                 "Default is the working project subfolder testbeds "
                 "[NOSE_TESTBED_DIR]")

    def configure(self, options, conf):
        super(Testbed, self).configure(options, conf)

    def finalize(self, result):
        pass

