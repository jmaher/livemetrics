from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import glob
import unittest
import argparse
import os
import sys
import json

class LiveMetricsOptions(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('-t', '--testPath', dest='testPath', action='store',
                        default='.', help='Path to the test manifest.')

        self.add_argument("--tests", action="append", 
                        default=[], help="Name of test to be included.")

        self.add_argument("-b", "--binary", action="store", 
                        help="Absolute path to application, overriding default.")

        self.add_argument("--logFile", action="store", 
                        metavar="FILE", default='livemetrics.log',
                        help="File to which logging occurs.")

        self.add_argument("-p", "--profilePath", action="store", default=None,
                        help="Path to the profile to use. If none specified, a temporary profile is created.")

        self.add_argument("-c", "--credentials", action="store", default=None,
                        help="Path to the json file containing credentials.")

        self.add_argument("-i", "--iterations", action="store", type=int, default=1,
                        help="Number of times to run the test.")

        self.add_argument("--wrapper", action="store", default=None,
                        help="Wrapper program to run around browser.")

        self.add_argument("--wrapperArgs", action="store", default=None,
                        help="Args to run wrapper program with.")

        self.add_argument("--configFile", action="store", default=None,
                        help="Filename which contains all the commandline options.")

    def verifyOptions(self, options):
        """ verify correct options and cleanup paths """
        if options.configFile and os.file.exists(configFile):
            try:
                with open(options.configFile, 'r') as config:
                    c = json.load(config)
                for option in options:
                    if option in c:
                        options.option = c.option
            except:
                print "ERROR: config file %s is not a valid json file" % options.configFile
                return None

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
    args = parser.parse_args()
    options = parser.verifyOptions(args)
    if options is None:
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

    iter = 0
    logname = '.'.join(options.logFile.split('.')[0:-1])
    logext = options.logFile.split('.')[-1]
    while (iter < options.iterations):
        iter += 1
        logFile = "%s-%s.%s" % (logname, iter, logext)
        #HACK: the test case in setUp() will parse sys.argv[1:], so we define our args
        del sys.argv[1:]
        sys.argv.append(options.binary)
        sys.argv.append(logFile)
        sys.argv.append(options.profilePath)
        sys.argv.append(options.credentials)

        text_runner = unittest.TextTestRunner().run(testSuite)

if __name__ == "__main__":
    main()



