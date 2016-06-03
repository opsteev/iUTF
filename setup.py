import glob
import io
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_description = '''
iUTF is a Unit Test framework for networking devices like switch, router, controller, ap.
And also it can remote control linux and mac via telnet or ssh.

It converts the prompt of devices to nodes and combines the nodes to a graph, then use the 
shortest path algorithm to find the path switching between nodes.

iUTF requires pexpect, nose, logging.
'''

setup(
    description='iUTF allows easy control of networking devices',
    author='Feng Ding',
    long_description=long_description,
    url='',
    author_email='feng.ding2@hpe.com',
    version='0.1',
    install_requires=['nose-html-reporting', 'pexpect', 'logging'],
    packages=['iut'],
    name='iutf',
    data_files=[
        ('testbeds', ['testbeds/testbed1']),
        ('tests', ['tests/__init__.py', 'tests/test_cusCalledStationID.py'])
    ],
    entry_points={
        'nose.plugins.0.10': [
            'testbed = iut.testbed_noseplugin:Testbed'
        ]
    }
    )