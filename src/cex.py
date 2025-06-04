import platform
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from dotenv import load_dotenv

def infer_default_browser():
    if platform.system() == "Windows":
        return webdriver.Chrome()
    elif platform.system() == "Darwin":
        return webdriver.Chrome()
    else:
        return webdriver.Firefox()
    
def check_element_presence(driver, locator, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(*locator)) > 0
        )
        return True
    except:
        return False
    
driver = infer_default_browser()

driver.get("https://uk.webuy.com")
WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "header-account-button")))
WebDriverWait(driver, 10).until(
    lambda d: d.execute_script("""
        const el = document.querySelector("#cmpwrapper");
        return el && el.shadowRoot && el.shadowRoot.querySelector(".cmpboxbtn.cmpboxbtnyes.cmptxt_btn_yes");
    """)
)

shadow_button = driver.execute_script("""
    return document
        .querySelector("#cmpwrapper")
        .shadowRoot
        .querySelector(".cmpboxbtn.cmpboxbtnyes.cmptxt_btn_yes");
""")

driver.execute_script("arguments[0].click();", shadow_button)

login_span = driver.find_element(By.XPATH, "//span[contains(@class, 'header-account-button')]")
login_span.click()

load_dotenv()
email = os.getenv("EMAIL")
pword = os.getenv("PASSWORD")
WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.ID, "email")))
input_email = driver.find_element(By.ID, 'email')
input_email.send_keys(email)
input_pword = driver.find_element(By.ID, "password")
input_pword.send_keys(pword)

print("Please sign in")
WebDriverWait(driver, 300).until(expected_conditions.element_to_be_clickable((By.XPATH, "//a[text()='View All']")))

target_page = "https://uk.webuy.com/user/account?tab=favourites&page=1&sortBy=most-recent"
driver.get(target_page)
WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "cx-account-card-grid")))
product_on_page = driver.find_elements(By.XPATH, "//a[contains(@class, 'line-clamp')]")
product_links = [[item.text, item.get_attribute("href")] for item in product_on_page]
max_pages = int(driver.find_elements(By.XPATH, "//ul/li/span[@class='page-link']")[-1].text)

if max_pages > 1:
    for i in range(2, max_pages+1):
        driver.get(f"https://uk.webuy.com/user/account?tab=favourites&page={i}&sortBy=most-recent")
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "line-clamp")))
        product_on_page = driver.find_elements(By.XPATH, "//a[contains(@class, 'line-clamp')]")
        product_links.extend([[item.text, item.get_attribute("href")] for item in product_on_page])

with open("data/favourites.csv", "w", newline='') as f:
    favourites_writer = csv.writer(f)
    favourites_writer.writerows(product_links)

driver.quit()