from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

def check_element_presence(driver, locator, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(*locator)) > 0
        )
        return True
    except:
        return False
    
driver = webdriver.Chrome()

driver.get("https://uk.webuy.com/product-detail?id=5026555431835&categoryName=PLAYSTATION5-GAMES&superCatName=GAMING&title=&queryID=59B82598F0384E22B02FEA6D6CFCEE2A&position=4")
WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "cx-link")))
locate_cookie_popup = (By.ID, "onetrust-accept-btn-handler")

if check_element_presence(driver, locate_cookie_popup):
    cookie_accept = driver.find_element(*locate_cookie_popup)
    cookie_accept.click()

check_stock_in_store = driver.find_element(By.XPATH, "//span[contains(@class, 'cx-link')]")
check_stock_in_store.click()

WebDriverWait(driver, 3).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "icon-text-button")))
all_stores_button = driver.find_element(By.XPATH, "//button[.//span[text()='All Stores']]")
all_stores_button.click()

WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "store-card")))
all_stores = driver.find_elements(By.CSS_SELECTOR, "a.store-card")
print(len(all_stores))
locations = [store.find_element(By.CSS_SELECTOR, "span:first-of-type").text for store in all_stores]
print(locations)