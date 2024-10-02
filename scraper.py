import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_exchange_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')

        headers = [header.text.split()[0].strip() for header in table.find_all('th')]
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cells = row.find_all('td')
            if cells:  # Only process rows with cells
                rows.append([cell.text.strip() for cell in cells])

        # Create a DataFrame from the rows
        df = pd.DataFrame(rows, columns=headers)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None