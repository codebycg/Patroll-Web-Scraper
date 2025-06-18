import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def contest_title(contestlink,driver):
    
    #use contest link to get the title of the contest
    #Here is an example of a link you would recieve as a function parameter: https://patroll.unifiedpatents.com/contests/mJ5QT4wkDCCjhy9xb

    driver.get(contestlink)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    #locate each contest
    h1 = soup.find("h1")
     
    if h1:
        title = h1.text.strip()
    else:
        title = 0
    print(title)
    return title
