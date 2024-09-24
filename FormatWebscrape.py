from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Path to the chromedriver executable
CHROMEDRIVER_PATH = "chromedriver.exe"

# Create options instance
options = Options()
options.headless = True
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

# Function to scrape links from a single page
def scrape_page(page_number):
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    url = f'https://www.ddproperty.com/en/property-for-sale/{page_number}?freetext=Bangkok&property_type=N&property_type_code%5B0%5D=CONDO&region_code=TH10&search=true'
    links = []

    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'nav-link'))
        )
        elements = driver.find_elements(By.CLASS_NAME, 'nav-link')
        links = [elem.get_attribute("href") for elem in elements if elem.get_attribute("href")]
        print(f"Scraped page {page_number}: {len(links)} links found.")
    except Exception as e:
        print(f"Error loading page {page_number}: {e}")
    finally:
        driver.quit()

    return links

def scrape_all_pages(start_page, end_page):
    all_links = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust the max_workers as needed
        futures = {executor.submit(scrape_page, page_number): page_number for page_number in range(start_page, end_page + 1)}
        
        for future in as_completed(futures):
            page_number = futures[future]
            try:
                result = future.result()
                all_links.extend(result)
            except Exception as e:
                print(f"Error with page {page_number}: {e}")

    return all_links

# Run the scraping function
start_time = datetime.now()
all_condo_links = scrape_all_pages(1, 1)
time_elapsed = datetime.now() - start_time 
print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

# Print the total number of links
print("Total condo listings = " + str(len(all_condo_links)))

# Save the links to a text file
with open("condo_links_all.txt", "w") as f:
    f.write("\n".join(all_condo_links))

print("Scraping completed and links saved to file.")
