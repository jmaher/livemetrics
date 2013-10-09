from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import glob
import unittest

def main():
    test_file_strings = glob.glob('test_*.py')
    module_strings = [str[0:len(str)-3] for str in test_file_strings]
    suites = [unittest.defaultTestLoader.loadTestsFromName(str) for str
              in module_strings]

    testSuite = unittest.TestSuite(suites)
    text_runner = unittest.TextTestRunner().run(testSuite)

if __name__ == "__main__":
    main()



