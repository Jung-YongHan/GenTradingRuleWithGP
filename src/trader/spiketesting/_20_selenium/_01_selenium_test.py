from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time


print("0")
cService = webdriver.ChromeService(executable_path='../../resource/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service = cService)

print("1")
driver.implicitly_wait(15) # 묵시적 대기, 활성화를 최대 15초가지 기다린다.
print("2")

# 페이지 가져오기(이동)
driver.get("http://192.168.1.173:9102/main")

driver.find_element(By.ID, "nav-login-btn").click()
driver.find_element(By.ID, "login-id").send_keys("jipsin08@gmail.com")
driver.find_element(By.ID, "login-pw").send_keys("1111")
# search = driver.find_element_by_css_selector('#login-btn-big')
# search.send_keys(Keys.Enter)
driver.find_element(By.ID, "login-btn-big").click()

time.sleep(5)
driver.find_element(By.ID, "logout-btn").click()
time.sleep(5)

# 5초후 종료
time.sleep(5)
print("4")
driver.quit() # 웹 브라우저 종료. driver.close()는 탭 종료

print("done")