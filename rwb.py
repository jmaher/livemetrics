import argparse
import ConfigParser
import glob
import os
import re
import shlex
import sys
import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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

    def overloadWithConfig(self, options, filename):
        try:
            config = ConfigParser.ConfigParser()
            config.read([options.configFile])
        except Exception, e:
            print "ERROR: config file %s is not a valid ini file" % options.configFile
            raise

        opts = argparse.Namespace()
        args = vars(options)
        for item in args:
            try:
                cfgitem = config.get('livemetrics', item)
                if item == 'tests':
                    cfgitem = [x.strip() for x in cfgitem.split(',')]
                    print cfgitem
            except:
                cfgitem = args[item]
            setattr(opts, item, cfgitem)
        return opts

    def verifyOptions(self, options):
        """ verify correct options and cleanup paths """
        if options.configFile and os.path.exists(options.configFile):
            options = self.overloadWithConfig(options, options.configFile)
            print options

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
        if options.wrapper and options.wrapperArgs:
           if not os.path.isfile(options.wrapper):
                print "ERROR: --wrapper must point to a valid binary"
                return None

        options.iterations = int(options.iterations)
        return options

def createWrapper(options, logfile):
    shellscript = 'wrapper.cmd'
    if options.wrapper and options.wrapperArgs:
        if options.binary is not shellscript:
            options.rawBinary = options.binary
        wrapperArgs = options.wrapperArgs.replace('{log}', "wrapped.%s"  % logfile)
        wrapperArgs = wrapperArgs.replace('{binary}', options.rawBinary)

        #NOTE: this only works on windows
        with open(shellscript, 'w') as pf:
            pf.write('"%s" %s' % (options.wrapper, wrapperArgs))
        options.binary = shellscript

def getTestName(filename):
    testname = ''
    #TODO: make this more robust
    testre = re.compile('test_(.*).py')
    m = testre.match(filename)
    testname = m.group(1)
    return testname

def main():
    parser = LiveMetricsOptions()
    args = parser.parse_args()
    options = parser.verifyOptions(args)
    if options is None:
        return 2

    test_modules = None
    if len(options.tests) == 0:
        test_files = glob.glob('test_*.py')
    else:
        test_files = []
        for test in options.tests:
            test_files.append("test_%s.py" % test)

    iter = 0
    logname = '.'.join(options.logFile.split('.')[0:-1])
    logext = options.logFile.split('.')[-1]
    while (iter < options.iterations):
        iter += 1

        for test in test_files:
            testname = getTestName(test)
            logFile = "%s-%s-%s.%s" % (logname, testname, iter, logext)
            createWrapper(options, logFile)
            print logFile

            #HACK: the test case in setUp() will parse sys.argv[1:], so we define our args
            del sys.argv[1:]
            sys.argv.append(options.binary)
            sys.argv.append(logFile)
            sys.argv.append(options.profilePath)
            sys.argv.append(options.credentials)

            suites = [unittest.defaultTestLoader.loadTestsFromName('test_%s' % testname)]
            testSuite = unittest.TestSuite(suites)
            text_runner = unittest.TextTestRunner().run(testSuite)

if __name__ == "__main__":
    main()



