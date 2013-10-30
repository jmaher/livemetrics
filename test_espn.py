import time
from testBenchmark import tBenchmark

class test_espn(tBenchmark):
    def test_espn(self):
        self.url = "espn.go.com"
        self.driver.get("http://%s" % self.url)
        self.driver.execute_script("collectorRecord();")

        try:
            elem = self.driver.find_element_by_link_text('NASCAR')
            elem.click()
            time.sleep(5.0)
            content = self.driver.find_element_by_id('content-wrapper')
        except Exception, e:
            print "ERROR: didn't find link for %s: %s" % (self.url, e)
            return

        for i in range(4):
            content.send_keys(' ')
            time.sleep(1.5)

        self.driver.execute_script("collectorStop();")
        self.driver.execute_script("collectorDump();")

