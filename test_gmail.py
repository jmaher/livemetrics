import time
from testBenchmark import tBenchmark

class test_gmail(tBenchmark):

    def test_gmail(self):
        self.url = "mail.google.com"
        self.name = "gmail"

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

        elem = self.driver.find_element_by_id('gmail-sign-in')
        elem.click()

        time.sleep(2.0)
        username = self.driver.find_element_by_id('Email')
        username.send_keys(credentials['username'])

        time.sleep(2.0)
        password = self.driver.find_element_by_id('Passwd')
        password.send_keys(credentials['password'])

        time.sleep(2.0)
        self.driver.find_element_by_id("signIn").click()

        time.sleep(3)
        #TODO: navigate around the site a bit, lots of clicking
        self.driver.find_element_by_link_text('Sent Mail').click()
        time.sleep(3)
        self.driver.find_element_by_link_text('Inbox').click()
        time.sleep(3)

        self.driver.execute_script("collectorStop();")
        self.driver.execute_script("collectorDump();")

