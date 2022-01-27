import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, tag

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait


@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
class BaseTestCase(StaticLiveServerTestCase):
    """
    Provides base test class which connects to the Docker
    container running selenium.
    """
    host = '0.0.0.0'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = socket.gethostbyname(socket.gethostname())
        print(socket.gethostname())
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
        )
        # cls.selenium.implicitly_wait(5.0)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


class AdminTest(BaseTestCase):
    host = socket.gethostbyname(socket.gethostname())

    def test_login(self):
        """
        As a superuser with valid credentials, I should gain
        access to the Django admin.
        """

        self.driver = self.selenium
        self.driver.get(f"http://{self.host}:8000/admin/login/?next=/admin/")
        self.driver.set_window_size(974, 893)
        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password").send_keys("testpasswd")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
