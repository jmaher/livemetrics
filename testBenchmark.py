from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest

class tBenchmark(unittest.TestCase):

    def setUp(self):
        # setup profile
        # use prefs file
        # support addons
        # add custom addon for record/reset/stop/collect/gc as a sample interface
        self.profile = webdriver.FirefoxProfile()
        prefs = {'mfl.logfile': '/home/jmaher/rwb/rwb.log',
                 'browser.dom.window.dump.enabled': True}
        for pref in prefs:
            self.profile.set_preference(pref, prefs[pref])

        addons = ['collector/collector.xpi']
        for addon in addons:
            self.profile.add_extension(extension=addon)

        # firefox app definition
        self.driver = webdriver.Firefox(self.profile)

    def tearDown(self):
        self.driver.quit()

