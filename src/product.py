import csv
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

def check_element_presence(driver, locator, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(*locator)) > 0
        )
        print(f"Found element")
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
WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "header-account-button")))
#locate_cookie_popup = (By.XPATH, "//a[contains(., 'Accept All Cookies')]")

WebDriverWait(driver, 30).until(
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

products_in_local_store = {}
products_not_in_local_store = []
products_out_of_stock = []

for i, (item, url) in enumerate(tqdm(favourites_list)):
    driver.get(url)
    WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[text()='Collect today, check store stock' or text()='Pick up unavailable']")))
    check_stock_in_store = driver.find_element(By.XPATH, "//span[text()='Collect today, check store stock' or text()='Pick up unavailable']")

    sell_price = float(driver.find_element(By.CLASS_NAME, "sell-price").text[1:])
    page = (len(favourites_list)-i) // 6
    #item_no_on_page = (len(favourites_list)-i) % 6

    if check_stock_in_store.text == 'Pick up unavailable':
        products_out_of_stock.append((item, sell_price, page))
        #to_write.append(f"{item} - Out of stock\n")
    else:
        check_stock_in_store.click()

        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "icon-text-button")))
        all_stores_button = driver.find_element(By.XPATH, "//button[.//span[text()='All Stores']]")
        all_stores_button.click()

        WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "store-card")))
        all_stores = driver.find_elements(By.CSS_SELECTOR, "a.store-card")
        locations = [store.find_element(By.CSS_SELECTOR, "span:first-of-type").text for store in all_stores]
        is_in_local_store = [s for s in locations if any(sub in s for sub in local_stores)]

        if is_in_local_store:
            for store in is_in_local_store:
                if store in products_in_local_store:
                    products_in_local_store[store].append((item, sell_price, page))
                else:
                    products_in_local_store[store] = [(item, sell_price, page)]
            #available_stores_as_str = ", ".join(is_in_local_store)
            #to_write.append(f"{item} - {available_stores_as_str}\n")
        else:
            products_not_in_local_store.append((item, sell_price, page))
            #to_write.append(f"{item} - Not available in local stores\n")

to_write = ["---------- Products in local store(s) ----------\n"]
for store, items in sorted(products_in_local_store.items(), key=lambda x: x[0]):
    to_write.append(f"{store} - £{sum(sell_price[1] for sell_price in items):.2f}\n")
    to_write.extend([f"\t{item} - £{sell_price:.2f} - P{page}\n" for item, sell_price, page in sorted(items, key=lambda x: x[0])])

to_write.append("\n---------- Products not in local store ----------\n")
to_write.extend([f"\t{item} - £{sell_price:.2f} - P{page}\n" for item, sell_price, page in sorted(products_not_in_local_store, key=lambda x: x[0])])

to_write.append("\n---------- Products out of stock ----------\n")
to_write.extend([f"\t{item} - £{sell_price:.2f} - P{page}\n" for item, sell_price, page in sorted(products_out_of_stock, key=lambda x: x[0])])

with open("data/results.txt", "w") as f:
    f.writelines(to_write)

driver.quit()