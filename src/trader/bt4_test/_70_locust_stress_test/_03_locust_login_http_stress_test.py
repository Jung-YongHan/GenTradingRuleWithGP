from locust import TaskSet, task, HttpUser, between


class UserBehavior(TaskSet) :
    def on_start(self) :
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def on_stop(self) :
        """ on_stop is called when the TaskSet is stopping """
        self.logout()

    def login(self) :
        response = self.client.post("/auth/jwt/login", {"username" : "jipsin08@gmail.com","password" : "1111"})

        print(f"{response=}")

        # Extract JWT token from response
        self.access_token = response.json().get("access_token")
        self.refresh_token = response.json().get("refresh_token")

        if self.access_token :
            print("Login successful, token received.")
        else :
            print("Login failed.")

    # @task(2)
    # def protected_request(self) :
    #     """Simulate a request to a protected endpoint using JWT."""
    #     if not self.access_token :
    #         self.login()
    #
    #     headers = {
    #         "Authorization" : f"Bearer {self.access_token}"
    #     }
    #
    #     response = self.client.get("/api/protected", headers = headers)
    #     if response.status_code == 200 :
    #         print("Protected request successful.")
    #     else :
    #         print("Protected request failed with status code:", response.status_code)

    @task(1)
    def logout(self) :
        """Simulate a logout request."""
        if not self.access_token :
            self.login()

        headers = {
            "Authorization" : f"Bearer {self.access_token}"
        }

        response = self.client.post("/auth/jwt/logout", headers = headers)
        if response.status_code == 200 or  response.status_code == 204:
            print("Logout successful.")
            self.access_token = None
        else :
            print("Logout failed with status code:", response.status_code)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    # host = "http://192.168.1.21:9102"
    host = "http://192.168.1.173:8097"



## 1. start locust
## locust -f .\_03_locust_login_http_stress_test.py