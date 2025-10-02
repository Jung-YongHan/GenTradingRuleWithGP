# locustfile.py
from locust import HttpUser, task, between, TaskSet


class UserBehavior(TaskSet):
    @task
    def get_user_detail(self):
        user_id = 1
        response = self.client.get(f'/market-report/cbf03663-ba81-4a2d-b257-46ce9131b4ab/100bc211-b769-4a15-89cb-284579307554', catch_response=True)
        print(f"market_report header: {response.headers}")
        print(f"market_report status code: {response.status_code}")

    @task
    def home(self):
        self.client.get('/')


class LocustUser(HttpUser):
    host = "http://192.168.1.173:9102/"
    tasks = [UserBehavior]
    wait_time = between(1, 4)

## Run
# locust -f ./_01_basic_locust.py