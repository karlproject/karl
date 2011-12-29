import unittest
from urlparse import urljoin

from selenium import webdriver

base_url = "http://localhost:6543/pg/"

class BlogFunctionalTests(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Remote(
            "http://localhost:4444/wd/hub",
            webdriver.DesiredCapabilities.HTMLUNITWITHJS)
        self._login("admin", "admin")

    def tearDown(self):
        self.driver.quit()

    def _css(self, css_sel):
        el = self.driver.find_element_by_css_selector(css_sel)
        return el

    def _setField(self, field_css, field_value):
        el = self._css(field_css)
        el.send_keys(field_value)
        return el

    def _login(self, un, pw):
        url = urljoin(base_url, 'logout.html')
        self.driver.get(url)
        url = urljoin(base_url, 'login.html')
        self.driver.get(url)
        self._css("#username").send_keys(un)
        el = self._css("#password")
        el.send_keys(pw)
        el.submit()
        self.assertEqual(self.driver.title, "Active KARL Communities")

    def test_communities_view(self):
        url = urljoin(base_url, 'communities')
        self.driver.get(url)
        self.assertEqual(
            self._css("#menubar-1 span").text,
            "Add Community")

    def test_office_folder_advanced_view(self):
        # This is for LP 909119
        url = urljoin(base_url,
                      'offices/files/network-news/advanced.html')
        self.driver.get(url)
        el = self._css('.kscreentitle')
        self.assertEqual(el.text, "Advanced Settings for Network News")