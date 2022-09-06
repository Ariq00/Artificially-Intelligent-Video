import pytest
import time
from selenium.webdriver.common.by import By
from tests.test_upload import delete_document


@pytest.mark.usefixtures('driver', 'run_app')
class TestSmartVideoBrowser:
    def test_watson_query(self):
        self.driver.get("http://127.0.0.1:5000/")

        youtube_url = 'https://www.youtube.com/watch?v=OFG_OoiMhWE'
        self.driver.find_element(By.ID, "youtubeUrl").send_keys(youtube_url)
        self.driver.find_element(By.ID, "youtubeButton").click()

        # search for concept
        time.sleep(3)
        self.driver.find_element(By.XPATH,
                                 "/html/body/main/div/section[1]/div/div[2]/div[2]/div/div[3]/input").send_keys(
            "When does the video talk about microwaves?")
        self.driver.find_element(By.XPATH,
                                 "/html/body/main/div/section[1]/div/div[2]/div[2]/div/div[3]/button").click()
        time.sleep(5)
        # check timestamp is correct
        response = self.driver.page_source
        delete_document(response)
        assert "0:05" in response  # checking 0:05 is returned as response to query

    def test_logged_out_navbar(self):
        self.driver.get("http://127.0.0.1:5000/")
        assert "Login" in self.driver.page_source

    def test_feature_cards(self):
        self.driver.get("http://127.0.0.1:5000/")
        assert "Sign up to Also Get These Features!" in self.driver.page_source
