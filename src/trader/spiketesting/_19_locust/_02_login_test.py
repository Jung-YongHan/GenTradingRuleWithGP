import time

from locust import HttpUser, TaskSet, task, between
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class UserBehavior(TaskSet):

    def on_start(self):
        service = webdriver.ChromeService(executable_path = '../../resource/chromedriver-win64/chromedriver.exe')
        self.driver = webdriver.Chrome(service = service)

        self.driver.get("http://192.168.1.173:9102/")
        # self.login()
        self.driver.implicitly_wait(15)


    @task(1)
    def perform_login_logout(self):
        self.driver.find_element(By.ID, "nav-login-btn").click()
        self.driver.find_element(By.ID, "login-id").send_keys("jipsin08@gmail.com")
        self.driver.find_element(By.ID, "login-pw").send_keys("1111")
        self.driver.find_element(By.ID, "login-btn-big").click()
        time.sleep(0.5)

        self.driver.find_element(By.ID, "logout-btn").click()
        time.sleep(0.5)



    def on_stop(self):
        self.driver.quit()

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "http://192.168.1.173:9102"

# locust -f ./_02_login_test.py