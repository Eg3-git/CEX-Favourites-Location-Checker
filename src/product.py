import csv
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

with open("data/stores.txt") as f:
    local_stores = f.read().splitlines()

with open("data/favourites.csv") as f:
    favourites_writer = csv.reader(f)
    favourites_list = list(favourites_writer)

driver = webdriver.Chrome()
driver.get("https://uk.webuy.com")
WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "header-account-button")))
locate_cookie_popup = (By.ID, "onetrust-accept-btn-handler")

if check_element_presence(driver, locate_cookie_popup):
    cookie_accept = driver.find_element(*locate_cookie_popup)
    cookie_accept.click()

to_write = []   

for item, url in favourites_list:
    driver.get(url)
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//span[text()='Check stock in store' or text()='Pick up unavailable']")))
    check_stock_in_store = driver.find_element(By.XPATH, "//span[text()='Check stock in store' or text()='Pick up unavailable']")
    if check_stock_in_store.text == 'Pick up unavailable':
        to_write.append(f"{item} - Out of stock\n")
    else:
        check_stock_in_store.click()

        WebDriverWait(driver, 5).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "icon-text-button")))
        all_stores_button = driver.find_element(By.XPATH, "//button[.//span[text()='All Stores']]")
        all_stores_button.click()

        WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "store-card")))
        all_stores = driver.find_elements(By.CSS_SELECTOR, "a.store-card")
        locations = [store.find_element(By.CSS_SELECTOR, "span:first-of-type").text for store in all_stores]
        is_in_local_store = [s for s in locations if any(sub in s for sub in local_stores)]

        if is_in_local_store:
            available_stores_as_str = ", ".join(is_in_local_store)
            to_write.append(f"{item} - {available_stores_as_str}\n")
        else:
            to_write.append(f"{item} - Not available in local stores\n")

with open("data/results.txt", "w") as f:
    f.writelines(to_write)