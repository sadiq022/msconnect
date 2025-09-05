from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import json

options = Options()
options.headless = False
driver = webdriver.Chrome(options=options)

url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/?q=&cert=&admReq=&langExamPC=&langExamLC=&langExamSC=&degree%5B%5D=2&langDeAvailable=&langEnAvailable=&lang%5B%5D=2&modStd%5B%5D=&cit%5B%5D=&tyi%5B%5D=&ins%5B%5D=&fee=&bgn%5B%5D=&dat%5B%5D=&prep_subj%5B%5D=&prep_degree%5B%5D=&sort=4&dur=&limit=10&offset=&display=list&lvlEn%5B%5D=&subjectGroup%5B%5D=56&fos%5B%5D=&subjects%5B%5D="

driver.get(url)

# Accept cookies if popup appears
try:
    WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button#usercentrics-root button[data-testid='uc-accept-all-button']"))
    ).click()
    print("Accepted cookies.")
    time.sleep(1)
except Exception:
    print("No cookie popup found.")

time.sleep(6)  # Wait for content to load

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

num_pages = 2  # Set this as needed
id_counter = 1  # Start ID from 1

results = []
base_url = "https://www2.daad.de"

for page in range(num_pages):
    offset = page * 10
    page_url = f"https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/?q=&cert=&admReq=&langExamPC=&langExamLC=&langExamSC=&degree%5B%5D=2&langDeAvailable=&langEnAvailable=&lang%5B%5D=2&modStd%5B%5D=&cit%5B%5D=&tyi%5B%5D=&ins%5B%5D=&fee=&bgn%5B%5D=&dat%5B%5D=&prep_subj%5B%5D=&prep_degree%5B%5D=&sort=4&dur=&limit=10&offset={offset}&display=list&lvlEn%5B%5D=&subjectGroup%5B%5D=56&fos%5B%5D=&subjects%5B%5D="
    
    driver.get(page_url)
    print(f"Scraping page {page+1} with offset {offset}")
    # Accept cookies only on the first page
    if page == 0:
        try:
            WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#usercentrics-root button[data-testid='uc-accept-all-button']"))
            ).click()
            print("Accepted cookies.")
            time.sleep(1)
        except Exception:
            print("No cookie popup found.")
    time.sleep(6)  # Wait for content to load

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    for card in soup.find_all("div", class_="c-ad-carousel__visual"):
        course_link_tag = card.find("a", class_="js-course-detail-link")
        if not course_link_tag:
            continue

        course_title = ""
        university = ""
        location = ""
        course_url = ""
        language = ""
        beginning = ""
        duration = ""
        tuition_fees = ""

        rel_link = course_link_tag.get('href', '')
        if rel_link:
            course_url = base_url + rel_link

        title_tag = course_link_tag.find('span', class_='js-course-title')
        if title_tag:
            course_title = title_tag.get_text(strip=True)

        university_tag = course_link_tag.find('span', class_='js-course-academy')
        if university_tag:
            university = university_tag.get_text(strip=True).replace('•', '').strip()

        loc_tag = course_link_tag.find('span', class_='c-ad-carousel__subtitle--location')
        if loc_tag:
            location = loc_tag.get_text(strip=True)

        card_parent = card.parent
        content_div = None
        for sibling in card_parent.find_next_siblings("div"):
            detail = sibling.find("div", class_="c-ad-carousel__content-list")
            if detail:
                content_div = detail
                break
        if not content_div:
            content_div = card_parent.find("div", class_="c-ad-carousel__content-list")

        if content_div:
            for li in content_div.find_all("li"):
                header = li.find("h3")
                value = li.find("span", class_="c-ad-carousel__data-item")
                if not (header and value): continue
                htxt = header.get_text(strip=True).lower()
                vtxt = value.get_text(strip=True)
                if "language" in htxt:
                    language = vtxt
                elif "beginning" in htxt:
                    beginning = vtxt
                elif "duration" in htxt:
                    duration = vtxt
                elif "tuition" in htxt:
                    tuition_fees = vtxt

        if course_title:
            results.append({
                'id': id_counter,  # Add unique ID here
                'course': course_title,
                'university': university,
                'location': location,
                'link': course_url,
                'language': language,
                'beginning': beginning,
                'duration': duration,
                'tuition_fees_per_semester': tuition_fees
            })
            id_counter += 1  # Increment for next entry

driver.quit()
print(json.dumps(results, indent=2, ensure_ascii=False))
with open("daad_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Scraped {len(results)} results with unique IDs. Data saved to daad_results.json.")