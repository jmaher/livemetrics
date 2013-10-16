from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import glob
import unittest
from optparse import OptionParser
import os
import sys
import json

class LiveMetricsOptions(OptionParser):
    def __init__(self, **kwargs):
        OptionParser.__init__(self, **kwargs)
        self.add_option("-t", "--test-path",
                        action="store", type="string", dest="testPath",
                        default='.', help="Path to the test manifest. "
                        "Defaults to current directory.")

        self.add_option("--test",
                        action="append", type="string", dest="tests",
                        default=[], help="Name of test to be included. "
                        "To include multiple tests, repeat this option.")

        self.add_option("-b", "--binary",
                        action="store", type="string", dest="binary",
                        help="absolute path to application, overriding default")

        self.add_option("--log-file",
                        action="store", type="string", dest="logFile",
                        metavar="FILE", default='livemetrics.log',
                        help="file to which logging occurs")

        self.add_option("-p", "--profile-path", action="store",
                        type="string", dest="profilePath",
                        default=None,
                        help="path to the profile to use. "
                             "If none specified, a temporary profile is created")

        self.add_option("-c", "--credentials", action="store",
                        type="string", dest="credentials",
                        default=None,
                        help="path to the json file containing credentials.")


        usage = """
                Usage instructions for runlive.py.
                %prog [options]
                All arguments except --binary are optional.
                """

        self.set_usage(usage)

    def verifyOptions(self, options):
        """ verify correct options and cleanup paths """
        if options.binary:
            if not os.path.isfile(options.binary):
                print "ERROR: --binary must specify the path to a browser"
                return None
        if not os.path.isdir(options.testPath):
            print "ERROR: --testPath must specify the path to a directory."
            return None
        if options.profilePath:
            if not os.path.isdir(options.profilePath):
                print "ERROR: --profilePath must specify the path to a directory."
                return None
        if options.credentials:
            if not os.path.isfile(options.credentials):
                print "ERROR: --credentials must point to a valid file"
                return None
            try:
                with open(options.credentials, 'r') as creds:
                    c = json.load(creds)
                site = c['credentials'][0]
            except:
                print "ERROR: %s is not a valid json file that we can understand" % options.credentials
                return None

        return options

def main():
    parser = LiveMetricsOptions()
    options, args = parser.parse_args()
    options = parser.verifyOptions(options)
    if options == None:
        return 2

    testSuite = unittest.TestSuite()
    if len(options.tests) == 0:
        test_modules = unittest.defaultTestLoader.discover(options.testPath, pattern='test_*.py')
        testSuite.addTests(test_modules)
    else:
        for test in options.tests:
            test_modules = unittest.defaultTestLoader.discover(options.testPath, pattern='test_*%s*.py' % test)
            if test_modules.countTestCases() == 0:
                print "error: test %s not found in directory %s/test_<name>.py" % (test, options.testPath)
                return 2
            testSuite.addTests(test_modules)

    command_line_args = options

    #HACK: the test case in setUp() will parse sys.argv[1:], so we define our args
    del sys.argv[1:]
    sys.argv.append(options.binary)
    sys.argv.append(options.logFile)
    sys.argv.append(options.profilePath)
    sys.argv.append(options.credentials)

    text_runner = unittest.TextTestRunner().run(testSuite)

if __name__ == "__main__":
    main()



