from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

from extract_contest_title import contest_title
from extract_prior_art import prior_art

# Set up headless Chrome browser
options = Options()

options.add_argument("--headless") 
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# Open the page
url = "https://patroll.unifiedpatents.com/contests?category=won"
driver.get(url)

# Initialize lists to store contest data
patentID = []  
priorArtID = []
contestTitles = []
contestLinks = []

prefix = 'https://www.google.com'
contestlink = 'https://patroll.unifiedpatents.com/'
max_pages = 19

# Create driver just for going into different webpages and scraping stuff, other driver is used for getting contest links
options = Options()

options.add_argument("--headless") 
options.add_argument("--window-size=1920,1080")
scraper = webdriver.Chrome(options=options)

try:
    for page_num in range(1, max_pages + 1):
        print(f"Processing page {page_num}...")
        
        time.sleep(1)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Locate each contest
        ul = soup.find("ul", class_="ant-list-items")
        
        if ul:
            # Find the links each sections goes to
            temp = [a['href'] for a in ul.find_all('a', href=True)]
            # Leaves only google patent links
            
            contest_link = ["https://patroll.unifiedpatents.com"+link for link in temp if link.startswith('/contests/')]
            
            patent_links = [link[31:] for link in temp if link.startswith(prefix)]
            patentID.extend(patent_links)
            contestLinks.extend(contest_link)
            
        else:
            break
            
        # Find the prior art, and contest title
        num = 1
        for a in contest_link:
            print(num)
            try:
                parsed_prior_art = prior_art(a, scraper)
            except:
                parsed_prior_art = []
            if parsed_prior_art is None:
                    parsed_prior_art = []
            
            prior_art_list = []
            for art in parsed_prior_art:
                prior_art_list.append({
                    "patent_id": art,
                    "country_code": art[:2]
                })
            priorArtID.append(prior_art_list)

            # priorArtID.append(0)
            contestTitles.append(contest_title(a, scraper))
            # contestTitles.append(0)
            num += 1
      
        # Clicks the next page and begins to repeat the same process
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
    scraper.quit()
    
    # Create structured data for JSON output
    contests_data = []
    
    # Make sure all lists are the same length to avoid index errors
    min_length = min(len(contestTitles), len(patentID), len(priorArtID), len(contestLinks))
    
    for i in range(min_length):
        contest_entry = {
            "contestTitle": contestTitles[i],
            "patentID": patentID[i],
            "priorArtID": priorArtID[i],
            "contestLink": contestLinks[i]
        }
        contests_data.append(contest_entry)
    
    # Create the final JSON structure
    json_output = {
        "contests": contests_data,
        "totalContests": len(contests_data),
        "scrapedPages": page_num
    }
    
    # Print the data (for debugging)
    print(contestTitles, patentID, priorArtID, contestLinks)
    
    # Save to JSON file
    output_filename = "won_patent_contests.json"
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(json_output, json_file, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to {output_filename}")
    print(f"Total contests scraped: {len(contests_data)}")


# The Scraper Evaluator code is below
import json

def simulated_patent_search(base_patent: str, winning_patents: list, prior_art_list: list):
    winning_set = set(p.upper() for p in winning_patents)
    found_set = set(p.upper() for p in prior_art_list)
    found_matches = list(winning_set & found_set)
    success = len(found_matches) > 0
    return found_matches, success

# Load JSON data
json_path = "won_patent_contests.json"
with open(json_path, 'r') as f:
    data = json.load(f)

# Extract scraped contests from JSON
scraped_contests = data.get("contests", [])

# Ground truth prior art for evaluation
ground_truth = {
    "US1234567B2": ["US7654321B1", "US9999999A1"],
    "US2468135B2": ["US1357924A1", "US9876543B2"],
    # Add more if known
}

# Initialize metrics
total = 0
success_count = 0
precision_scores = []
recall_scores = []

for contest in scraped_contests:
    contest_title = contest.get("contestTitle")
    troll_patent = contest.get("patentID")
    prior_art_str = contest.get("priorArtID", "")
    contest_link = contest.get("contestLink")
    
    if not troll_patent or troll_patent not in ground_truth:
        continue

    # Handle semicolon-separated prior art
    scraped_prior_art = [pat.strip().upper() for pat in prior_art_str.split(";") if pat.strip()]
    correct_prior_art = [p.upper() for p in ground_truth[troll_patent]]

    found, success = simulated_patent_search(troll_patent, correct_prior_art, scraped_prior_art)

    # Calculate precision and recall
    true_positives = len(found)
    precision = true_positives / len(scraped_prior_art) if scraped_prior_art else 0
    recall = true_positives / len(correct_prior_art) if correct_prior_art else 0

    precision_scores.append(precision)
    recall_scores.append(recall)

    if success:
        success_count += 1
    total += 1

# Compute final metrics
accuracy = (success_count / total) * 100 if total else 0
mean_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0
mean_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0

print(f"\n Evaluation Metrics:")
print(f"Total Contests Evaluated: {total}")
print(f"Success Rate: {accuracy:.2f}%")
print(f"Average Precision: {mean_precision:.2f}")
print(f"Average Recall: {mean_recall:.2f}")