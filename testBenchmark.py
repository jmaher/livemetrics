from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import unittest
import sys
import os
import json

class tBenchmark(unittest.TestCase):

    def setUp(self):
        self.binary = sys.argv[1]
        self.logFile = sys.argv[2]
        self.profilePath = sys.argv[3]

        self.credentials = {}
        try:
            with open(sys.argv[4], 'r') as creds:
                self.credentials = json.load(creds)
        except:
            pass        

        if self.profilePath and os.path.exists(self.profilePath):
            self.profile = webdriver.FirefoxProfile(self.profilePath)
        else:
            self.profile = webdriver.FirefoxProfile()

        # TODO: use prefs file
        prefs = {'mfl.logfile': self.logFile,
                 'browser.dom.window.dump.enabled': True}
        for pref in prefs:
            self.profile.set_preference(pref, prefs[pref])

        addons = ['collector.xpi']
        for addon in addons:
            self.profile.add_extension(extension=addon)

        if self.binary and os.path.exists(self.binary):
            binary = FirefoxBinary(self.binary)
            self.driver = webdriver.Firefox(firefox_profile=self.profile, firefox_binary=binary)
        else:
            self.driver = webdriver.Firefox(firefox_profile=self.profile)

    def tearDown(self):
        self.driver.quit()

