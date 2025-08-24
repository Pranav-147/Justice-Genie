import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random
import time

# MongoDB Connection Setup
client = MongoClient("mongodb://localhost:27017/doj_database")
db = client['doj_database']
collection = db['minister_data']

# URLs to scrape
urls = [
    "https://doj.gov.in/whos-who/",
    "https://doj.gov.in/citizens-charter/"
]

# List of User-Agent headers to simulate a browser request
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36",
    # Add more user agents as needed
]

def scrape_and_insert(url):
    retries = 5
    for _ in range(retries):
        try:
            headers = {'User-Agent': random.choice(user_agents)}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check for a successful request
            break  # Break if request is successful
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {url}: {e}. Retrying...")
            time.sleep(3)  # Wait 3 seconds before retrying
    else:
        print(f"Failed to fetch {url} after {retries} attempts.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', class_=['tabular-result-container', 'data-table-1'])

    for table in tables:
        headers = [header.get_text(strip=True) for header in table.find_all('th')]

        rows = []
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            if len(columns) == len(headers):
                row_data = {headers[i]: columns[i].get_text(strip=True) for i in range(len(columns))}
                rows.append(row_data)

        if rows:
            try:
                collection.insert_many(rows)
                print(f"Inserted {len(rows)} rows into the database from {url}")
            except Exception as e:
                print(f"Error inserting data into MongoDB from {url}: {e}")
        else:
            print(f"No data found in the table from {url}")

for url in urls:
    scrape_and_insert(url)

print("Data scraping and insertion complete.")
