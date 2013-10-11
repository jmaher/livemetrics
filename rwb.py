from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import glob
import unittest
from optparse import OptionParser
import os
import sys

class LiveMetricsOptions(OptionParser):
    def __init__(self, **kwargs):
        OptionParser.__init__(self, **kwargs)
        self.add_option("-t", "--test-path",
                        action="store", type="string", dest="testPath",
                        default=None, help="path to the test manifest")

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

        usage = """
                Usage instructions for runlive.py.
                %prog [options]
                All arguments except --binary are optional.
                """

        self.set_usage(usage)

    def verifyOptions(self, options):
        """ verify correct options and cleanup paths """
        if not options.binary:
            if not os.path.exists(options.binary):
                print "error: --binary must specify the path to a browser"
                return None
        return options

def main():
    parser = LiveMetricsOptions()
    options, args = parser.parse_args()
    options = parser.verifyOptions(options)
    if options == None:
        return 2

    test_file_strings = glob.glob('test_*.py')
    module_strings = [str[5:len(str)-3] for str in test_file_strings]
    testsToRun = module_strings
    if options.testPath:
        testsToRun = []
        for test in options.testPath:
            if test not in module_strings:
                print "error: test %s not found in these tests %s" % (test, module_strings)
                return 2
            testsToRun.append(test)

    suites = [unittest.defaultTestLoader.loadTestsFromName('test_' + str) for str
              in testsToRun]

    command_line_args = options

    #HACK: the test case in setUp() will parse sys.argv[1:], so we define our args
    del sys.argv[1:]
    sys.argv.append(options.binary)
    sys.argv.append(options.logFile)
    sys.argv.append(options.profilePath)

    testSuite = unittest.TestSuite(suites)
    text_runner = unittest.TextTestRunner().run(testSuite)

if __name__ == "__main__":
    main()



