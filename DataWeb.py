import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import concurrent.futures

class Scraper:
    def __init__(self):
        self.session = requests.Session()  

    def retrieve(self, link):
        try:
            page = self.session.get(link)
            soup = BeautifulSoup(page.content, 'html.parser')

            name_elem = soup.select_one("title")
            name = name_elem.get_text() if name_elem else "No name"

            pricesqm_elem = soup.select_one("meta-table__item__value-text")
            pricesqm = pricesqm_elem.get_text() if pricesqm_elem else "No price"

            unit_elem = soup.select_one("meta-table__item__value-text")
            unit = unit_elem.get_text() if unit_elem else "No unit"

#meta-table__item__value-text

            return (name, pricesqm, unit)
        except Exception as e:
            print(f"Error processing {link}: {e}")
            return None

# Function to process links using threading
def process_links(links, max_workers=20):
    scraper = Scraper()
    condo_list = []
    total_links = len(links)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_link = {executor.submit(scraper.retrieve, link): link for link in links}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_link), 1):
            data = future.result()
            if data is not None:
                condo_list.append(data)
            if i % 1000 == 0:  # Print progress every 1000 links
                print(f"Processed {i}/{total_links} links", end='\r', flush=True)

    print(f"Processing complete. Total links processed: {total_links}")
    return condo_list

# Function to read links from a text file
def read_links_from_file(file_path):
    with open(file_path, 'r') as file:
        links = [line.strip() for line in file.readlines()]
    return links

# Main function to execute the scraping and save the results
def main():
    file_path = 'condo_links_all_faster.txt'
    condo_links_all = read_links_from_file(file_path)

    start_time = datetime.now()

    # Process the links and get the condo details
    condo_list = process_links(condo_links_all)

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(condo_list, columns=['Name', 'SQM', 'Price'])
    df.to_csv("NewPrice.csv", header=['Name', 'SQM', 'Price'], index=False, encoding='utf-8-sig')

    print(f"Data saved, total valid entries: {len(condo_list)}")
    print(f'Time elapsed (hh:mm:ss.ms): {datetime.now() - start_time}')

if __name__ == "__main__":
    main()
