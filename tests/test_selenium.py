import pytest
import time


@pytest.mark.usefixtures('driver', 'run_app')
class TestRentAppBrowser:
    def test_app_is_running(self):
        self.driver.implicitly_wait(10)
        self.driver.get("http://127.0.0.1:5000/")
        time.sleep(3)
        assert self.driver.title == 'SmartVideo'
