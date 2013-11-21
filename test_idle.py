import time
from testBenchmark import tBenchmark

class test_idle(tBenchmark):
    def test_idle(self):
        self.url = "about:home"
        self.driver.get(self.url)
        self.driver.execute_script("collectorRecord();")

        time.sleep(30.0)

        self.driver.execute_script("collectorLog('stopping script');")
        self.driver.execute_script("collectorStop();")
        self.driver.execute_script("collectorDump();")

