import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor

# Load Excel data
file_path = 'Test2.xlsx' 
data = pd.read_excel(file_path)

# Initialize new columns for subdistrict, district, and location
data['New Subdistrict'] = ""
data['New District'] = ""
data['Location'] = ""  # New column for location

# Setup Selenium WebDriver
def create_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

# Function to search condo location
def search_condo_location(condo_name):
    driver = create_driver()
    # Modify the search URL to ensure English results
    search_url = f"https://www.google.com/search?q={condo_name}+location&hl=en"
    driver.get(search_url)

    # Allow time for results to load
    time.sleep(2)

    # Extract the location information from the search results
    try:
        result_element = driver.find_element(By.CLASS_NAME, "sXLaOe")  # Use the specified class
        location_text = result_element.text.strip()  # Store the entire text in "Location"
        return condo_name, location_text
    except Exception as e:
        print(f"Error retrieving location for {condo_name}: {e}")
        return condo_name, None
    finally:
        driver.quit()

# Main execution with ThreadPoolExecutor
total_condos = len(data)
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(search_condo_location, row['Name']): index for index, row in data.iterrows()}
    
    for index, future in enumerate(futures):
        condo_name, location = future.result()
        
        # Store the location text in the new column
        if location:
            data.at[futures[future], 'Location'] = location
        
        # Calculate and display progress percentage
        progress_percent = (index + 1) / total_condos * 100
        print(f"Progress: {progress_percent:.2f}%")

# Save the updated Excel file with new columns
output_file = 'Condo_Locations.xlsx'
data.to_excel(output_file, index=False)

print(f"Updated Excel file saved as {output_file}")
