# How to install
+ python 2.7 is required
+ pip install virtualenv
+ virtualenv --no-site-packages iutf
+ source iutf/bin/activate
+ pip install iutf-0.1-py2-none-any.whl

# How to run scripts
+ Must have a directory named tests in current directory
+ The scripts should be put into the directory 'tests'
+ Execute: nosetests --testbed &lt;testbed&gt;

# How to write a script
+ import all libs in tests/\_\_init\_\_.py
+ In the scripts:
+ Import libs: from tests import *
+ Import devices from testbed file: IAP1, IAP2, IAP3 = REQUEIRED('IAP1', 'IAP2', 'IAP3')
+ Write test cases: def test_...()
+ def setup is for preparation
+ def teardown is for cleanup

# Generate the report
#### Run with parameter:
+   nosetests --with-html --html-report=report.html --testbed &lt;testbed&gt;
