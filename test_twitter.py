import time
from testBenchmark import tBenchmark

class test_twitter(tBenchmark):

    def test_twitter(self):
        self.url = "twitter.com"
        self.name = "twitter"

        credentials = None
        try:
            for site in self.credentials["credentials"]:
                if site["name"] == self.name:
                    credentials = site
        except:
            pass

        if not credentials:
            print "ERROR: Unable to run %s test as it requires credentials" % self.name
            return

        if not credentials["username"] or not credentials["password"]:
            print "ERROR: Unable to run %s test as it requires username/password" % self.name
            return

        self.driver.get("https://%s" % self.url)
        self.driver.execute_script("collectorRecord();")

        try:
            content = self.driver.find_element_by_class_name('front-signin')
        except:
            print "ERROR: didn't find login form on: %s" % self.url
            return

        time.sleep(2.0)
        username = self.driver.find_element_by_id('signin-email')
        username.send_keys(credentials['username'])

        time.sleep(2.0)
        password = self.driver.find_element_by_id('signin-password')
        password.send_keys(credentials['password'])

        time.sleep(2.0)
        self.driver.find_element_by_class_name("primary-btn").click()

        #TODO: navigate around the site a bit, lots of clicking

        self.driver.execute_script("collectorStop();")
        self.driver.execute_script("collectorDump();")

