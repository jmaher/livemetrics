import time
from testBenchmark import tBenchmark

class test_yahoo(tBenchmark):
    def test_yahoo(self):
        self.url = "www.yahoo.com"
        self.driver.get("http://%s" % self.url)
        self.driver.execute_script("collectorRecord();")

        try:
            time.sleep(2.0)
            self.driver.find_element_by_link_text('News').click()
            time.sleep(2.0)
            self.driver.find_element_by_link_text('World').click()
            time.sleep(2.0)
            content = self.driver.find_element_by_id('yog-bd')
        except:
            print "ERROR: didn't find main page element for %s" % self.url
            return

        for i in range(10):
            content.send_keys(' ')
            time.sleep(1.5)

        self.driver.execute_script("collectorStop();")
        self.driver.execute_script("collectorDump();")

