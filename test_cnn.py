import time
from testBenchmark import tBenchmark

class test_cnn(tBenchmark):

    def test_cnn(self):
        self.url = "www.cnn.com"
        self.driver.get("http://%s" % self.url)
        self.driver.execute_script("collectorRecord();")

        try:
            content = self.driver.find_element_by_id('cnnMainPage')
        except:
            print "ERROR: didn't find main page element for %s" % self.url
            return

        for i in range(10):
            content.send_keys(' ')
            time.sleep(0.5)

        self.driver.execute_script("collectorStop();")
        self.driver.execute_script("collectorDump();")

