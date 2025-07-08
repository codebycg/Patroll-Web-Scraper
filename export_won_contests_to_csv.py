from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

from extract_contest_title import contest_title
from extract_prior_art import prior_art
from generate_excel_output import tocsv
# Set up headless Chrome browser
options = Options()

options.add_argument("--headless") 
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# Open the page
url = "https://patroll.unifiedpatents.com/contests?category=won"
driver.get(url)

patentID = []  
priorArtID=[]
contestTitles=[]
contestLinks=[]

prefix = 'https://www.google.com'
contestlink='https://patroll.unifiedpatents.com/'
max_pages = 19

#create driver just for going into different webpages and scrpaing stuff, other driver is used for getting contest links
options = Options()

options.add_argument("--headless") 
options.add_argument("--window-size=1920,1080")
scraper = webdriver.Chrome(options=options)
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
            
            contest_link = ["https://patroll.unifiedpatents.com"+link for link in temp if link.startswith('/contests/')]
            
            patent_links = [link[31:] for link in temp if link.startswith(prefix)]
            patentID.extend(patent_links)
            contestLinks.extend(contest_link)
            
        else:
            
            break
        #find the prior art, and contest title
        num=1
        for a in contest_link:
            print(num,a)
            try:
                priorArtID.append(prior_art(a,scraper))
            except:
                priorArtID.append(0)
            #priorArtID.append(0)
            contestTitles.append(contest_title(a,scraper))
            #contestTitles.append(0)
            num+=1
      
        #clicks the next page and begins to repeat the same process
        try:
            next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "li.ant-pagination-next[title='Next Page']"))
)
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            driver.execute_script("arguments[0].click();", next_button)
            print("Clicked the 'Next Page' button")
        except Exception as e:
            print(f"Could not find/click 'Next Page' button: {e}")
            break
        
finally:
    driver.quit()
    print(contestTitles,patentID,priorArtID,contestLinks)
    tocsv(contestTitles,patentID,priorArtID,contestLinks)
    
