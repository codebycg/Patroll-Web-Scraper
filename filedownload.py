from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Set up headless Chrome browser
options = Options()
options.add_argument("--headless") 
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# Open the page
url = "https://patroll.unifiedpatents.com/contests?category=finished"
driver.get(url)

all_links = []  
prefix = 'https://www.google.com'
max_pages = 20  

try:
    for page_num in range(1, max_pages + 1):
        print(f"Processing page {page_num}...")
        
        
        time.sleep(1)
        
        
        soup = BeautifulSoup(driver.page_source, "html.parser")

        #locate each contest
        ul = soup.find("ul", class_="ant-list-items")
        
        if ul:
            #find the links each sections goes to
            temp = [a['href'] for a in ul.find_all('a', href=True)]
            #leaves only google patent links
            links = [link for link in temp if link.startswith(prefix)]
            all_links.extend(links)
            print(f"Found {len(links)} links on page {page_num}")
        else:
            print("No <ul> element found")
            break

        #clicks the next page and begins to repeat the same process
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[contains(@title,'{page_num + 1}')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            driver.execute_script("arguments[0].click();", next_button)
            print(f"Clicked next page button (title={page_num + 1})")
        except Exception as e:
            print(f"Could not find/click next page button: {e}")
            break

finally:
    #all the links are written to file
    with open('patents.txt', 'w') as f:
        for link in all_links:
            f.write(f"{link}\n")
    print(f"Saved {len(all_links)} total links to patents.txt")
    
    driver.quit()