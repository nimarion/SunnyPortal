from datetime import datetime, timedelta
import json
import time
import sys
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path


if platform.system() == "Linux":
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(800, 800))
    display.start()

chrome_prefs = {
    "profile.default_content_settings.popups": 0,
    "download.default_directory": str(Path.cwd())  # Assuming you've imported the 'Path' class from pathlib
}

options = Options()
options.add_experimental_option("prefs", chrome_prefs)
options.add_argument("--window-size=800,800")
options.add_argument("--disable-gpu")
options.add_argument("--lang=en-US")
options.add_argument("--remote-allow-origins=*")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def perform_login(email, password):
    driver.get("https://www.sunnyportal.com/")
    current_url = driver.current_url
    password_element = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    email_element = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    if not (password_element and email_element):
        return
    
    email_element.send_keys(email);
    password_element.send_keys(password);
    
    wait = WebDriverWait(driver, 15)
    accept_cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
    accept_cookies.click()
    submit_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))
    submit_element.click()

    wait.until_not(EC.url_to_be(current_url))

    if current_url == driver.current_url:
        raise RuntimeError("Login failed")

def load_forecast():
    driver.get("https://www.sunnyportal.com/HoMan/Forecast/LoadRecommendationData")
    json_element = driver.find_element(By.TAG_NAME, "pre")
    json_text = json_element.text
    payload_forecasts = json.loads(json_text)
    file_path = Path("forecast.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(payload_forecasts, file, ensure_ascii=False, indent=4)

def load_current(date_list):
    driver.get("https://www.sunnyportal.com/FixedPages/HoManEnergyRedesign.aspx");
    wait = WebDriverWait(driver, 15)
    time_range = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_UserControlShowHoManEnergyRedesign_ChartDatePicker_PC_DatePickerFrom")))
    for date in date_list:
        time_range.clear()
        time_range.send_keys(date)
        time_range.send_keys(Keys.ENTER)
        time.sleep(2)
        driver.get(f"https://www.sunnyportal.com/PortalCharts/Core/PortalChartsAPI.aspx?id=mainChart&mode=last_info&t={int(time.time())}")
        time.sleep(2)

def generate_date_list(start_date, end_date):
    delta = end_date - start_date
    return [(start_date + timedelta(days=i)).strftime("%m/%d/%Y") for i in range(delta.days + 1)]



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sunnyportal.py foo@bar.com password")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    
    perform_login(email, password)
    load_forecast()

    start_date =  datetime.today() - timedelta(days=1)
    end_date = datetime.today()
    date_list = generate_date_list(start_date, end_date)
    load_current(date_list)
    driver.quit()

