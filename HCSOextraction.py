# Last modified: 7/30/24
# Uses following libraries: requests for HTTP requests, beautifulsoup4 for parsing HTML content, 
# pandas for organizing the data, and openpyxl to create an excel file.

import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl
import re

def fetch_booking_reports(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return None
    return response.text

def parse_booking_reports(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    records = []
    
    exclude_phrases = [
        "Violation of probation",
        "Homeless",
        "Booked for previous charges or other reason",
        "Failure to appear",
        "Driving on",
        "Retaliation against",
        "Fugitive",
        "Driving under the influence",
        "Contraband in penal institutions",
        "Violation of protection order",
        "Violation of restraining order",
        "717 E 11th St"
    ]
    
    table = soup.find('table', class_='booking_reports_list')
    if not table:
        print("No table found on the page.")
        return records
    
    rows = table.find_all('tr')
    
    for row in rows[1:]:
        cell = row.find('td')
        if cell:
            strong_tags = cell.find_all('strong')
            name = strong_tags[0].text.strip() if strong_tags else ''
            
            # Extract address
            br_tags = cell.find_all('br')
            street = city = zip_code = ''
            if len(br_tags) >= 2:
                street = br_tags[0].next_sibling.strip() if br_tags[0].next_sibling else ''
                city_zip = br_tags[1].next_sibling.strip() if br_tags[1].next_sibling else ''
                
                if city_zip:
                    parts = city_zip.split(',')
                    if len(parts) == 2:
                        city = parts[0].strip()
                        zip_code = parts[1].strip()
            
            # Find the charges
            ul_tag = cell.find('ul')
            charges = ul_tag.get_text(separator=', ').strip() if ul_tag else ''
            
            # Check if any of the exclude phrases are in the charges or address text
            if not any(exclude_phrase.lower() in charges.lower() or exclude_phrase.lower() in street.lower() or exclude_phrase.lower() in city.lower() for exclude_phrase in exclude_phrases):
                records.append({'Name': name, 'Street': street, 'City': city, 'Zip Code': zip_code})
    
    return records

# Creates a new excel document with the data
def save_to_excel(records, filename='booking_reports.xlsx'): # Can change file name as needed
    df = pd.DataFrame(records)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    url = "http://www.hcsheriff.gov/cor/display.php?day=0"  # Can change link if needed (Extracting data from past days/0 for today, 1 for yesterday, etc.)
    html_content = fetch_booking_reports(url)
    if html_content:
        records = parse_booking_reports(html_content)
        save_to_excel(records)
