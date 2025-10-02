# You need to start selenium server first:
# Download it from https://www.seleniumhq.org/download/ and run it by executing:
# java -jar selenium-server-4.23.0.jar standalone
# Also, make sure you have installed chromedriver first. On macOS you would do: brew install --cask chromedriver
#
# You can also run selnium server via docker using the following example command:
# docker run -e SE_NODE_SESSION_TIMEOUT=60 -e SE_NODE_MAX_SESSIONS=5 -p 4444:4444 -p 7900:7900 --shm-size="2g" --rm selenium/standalone-chrome:96.0
# pylint: disable=import-error # sometimes selenium is not installed
import time
from locust import task, constant, events, run_single_user, between
from locust_plugins.users.webdriver import WebdriverUser
from locust_plugins.listeners import RescheduleTaskOnFail
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class MyUser(WebdriverUser):
    wait_time = constant(2)
    # webdriver client options can be customized by overriding the option_args
    option_args = [
        "--disable-translate",
        "--disable-extensions",
        "--disable-background-networking",
        "--safebrowsing-disable-auto-update",
        "--disable-sync",
        "--metrics-recording-only",
        "--disable-default-apps",
        "--no-first-run",
        "--disable-setuid-sandbox",
        "--hide-scrollbars",
        "--no-sandbox",
        "--no-zygote",
        "--autoplay-policy=no-user-gesture-required",
        "--disable-notifications",
        "--disable-logging",
        "--disable-permissions-api",
        "--ignore-certificate-errors",
    ]
    host = "http://192.168.1.173:9102"

    if __name__ == "__main__":
        # wait_time = constant(5)
        wait_time = between(5, 10)
    else:
        # headless by default if running real locust and not just debugging
        headless = False
        # headless = True

    def on_start(self):
        self.client.set_window_size(1400, 1200)
        self.client.implicitly_wait(5)

        self.login()

    def login(self):
        self.client.get(f"{MyUser.host}/main")

        move_login_page_elem = self.client.locust_find_element(By.ID, "login-btn", "move login page")
        self.client.execute_script("arguments[0].click();", move_login_page_elem)

        self.client.locust_find_element(By.ID, "login-id", name = "enter login-id").send_keys("jipsin08@gmail.com")
        self.client.locust_find_element(By.ID, "login-pw", name = "enter login-password").send_keys("1111")

        req_login_elem = self.client.locust_find_element(By.ID, "login-btn-big", name = "request to login")
        self.client.execute_script("arguments[0].click();", req_login_elem)

    @task
    def retrieve_strategy(self):
        self.clear()
        self.client.start_time = time.monotonic()  # to measure the time from now to first locust_find_element finishes
        scenario_start_time = self.client.start_time  # to measure the time for the whole scenario

        wait = WebDriverWait(self.client, 10, poll_frequency = 0.5)

        wait.until(EC.presence_of_element_located((By.ID, "stgy_card_1")))
        stgy_card_1_elem = self.client.locust_find_element(By.ID, "stgy_card_1", "retrieve 1st strategy")
        self.client.execute_script("arguments[0].scrollIntoView(true);", stgy_card_1_elem)
        stgy_card_1_elem.click()      ## click one strategy and see 리포트

        wait.until(EC.presence_of_element_located((By.ID, "condition-tab")))
        condition_tab_elem = self.client.locust_find_element(By.ID, "condition-tab", "condition tab")
        self.client.execute_script("arguments[0].click();", condition_tab_elem)

        tr_result_tab_elem = self.client.locust_find_element(By.ID, "tradingResult-tab", "trading result tab")
        self.client.execute_script("arguments[0].click();", tr_result_tab_elem)

        compare_tab_elem = self.client.locust_find_element(By.ID, "compare-tab", "compare tab")
        self.client.execute_script("arguments[0].click();", compare_tab_elem)

        optimization_tab_elem = self.client.locust_find_element(By.ID, "optimization-tab", "optimization tab")
        self.client.execute_script("arguments[0].click();", optimization_tab_elem) ## see AI 전략 최적화

        report_tab_elem = self.client.locust_find_element(By.ID, "report-tab", "report tab")
        self.client.execute_script("arguments[0].click();", report_tab_elem)  ## see report-tab

        wait.until(EC.presence_of_element_located((By.ID, "navigate-to-dashboard")))
        move_to_dashboard_elem = self.client.locust_find_element(By.ID, "navigate-to-dashboard", "move to my strategy room")
        self.client.execute_script("arguments[0].click();", move_to_dashboard_elem)  ## move to my strategy room

        self.client.implicitly_wait(0.5)

        self.environment.events.request.fire(
            request_type="flow",
            name="retrieve strategy flow(total)",
            response_time=(time.monotonic() - scenario_start_time) * 1000,
            response_length=0,
            exception=None,
        )

    def on_stop(self):
        self.client.locust_find_element(By.ID, "logout-btn", name = "logout").click()
        self.client.quit()

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    RescheduleTaskOnFail(environment)


# if __name__ == "__main__":
#     run_single_user(MyUser)

## How to Run
## 0. add path ./resource/chromedriver-win64

## 1. start selenium server
## java -jar selenium-server-4.23.0.jar standalone

## 2. start locust
## locust -f .\_02_locust_strategy_webui_stress_test.py