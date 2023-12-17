import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import sqlite3

# Create a SQLite database connection
conn = sqlite3.connect('eve_killboard.db')
cursor = conn.cursor()


# Function to insert data into the SQLite database with duplicate protection
def insert_data(system, ship_type, victim, victim_corporation, date, enemy_player, enemy_corporation, enemy_numbers):
    cursor.execute('''
        SELECT * FROM killboard
        WHERE system = ? AND ship_type = ? AND victim = ? AND date = ? AND enemy_player = ?
    ''', (system, ship_type, victim, date, enemy_player))
    existing_entry = cursor.fetchone()

    if existing_entry:
        print("Duplicate entry found. Skipping insertion.")
    else:
        cursor.execute('''
            INSERT INTO killboard (system, ship_type, victim, victim_corporation, date, enemy_player, enemy_corporation, enemy_numbers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (system, ship_type, victim, victim_corporation, date, enemy_player, enemy_corporation, enemy_numbers))
        conn.commit()
        print("Inserted new entry into the database.")


# Function to fetch and process data from the given URL
def process_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    date_elements = soup.find_all('tr', class_='tr-date')

    for date_element in date_elements:
        date = date_element['date']
        rows = date_element.find_all_next('tr', class_='killListRow')

        for row in rows:
            location_cell = row.find('td', class_='location')
            anchor = location_cell.find('a')

            if anchor and ('J1' in anchor.text or 'J2' in anchor.text):
                system_name = anchor.text

                victim_info = row.find('td', class_='victim')
                victim_name_anchor = victim_info.find('a', class_='wrapplease')
                victim_name = victim_name_anchor.text
                img_tag = row.find('img', class_='eveimage')
                victim_ship_type = img_tag['alt'] if img_tag else "Unknown"
                victim_corp = victim_info.find_all('a', class_='wrapplease')[1].text

                timestamp_cell = row.find('td', style='width: 55px;')
                timestamp_text = timestamp_cell.get_text(strip=True)
                time_part = timestamp_text.split('<br>')[0].strip()
                time_match = re.search(r'(\d{2}:\d{2})', time_part)

                if time_match:
                    hour, minute = map(int, time_match.group(1).split(':'))
                    datetime_obj = datetime.strptime(f"{date} {hour:02d}:{minute:02d}", "%b %d, %Y %H:%M")
                    formatted_datetime = datetime_obj.strftime("%d.%m.%Y %H:%M")

                    final_blow_info = row.find('td', class_='finalBlow hidden-xs finalBlowColumn')
                    enemy_player_name = final_blow_info.find('a', class_='wrapplease').text
                    enemy_corp_name = final_blow_info.find_all('a', class_='wrapplease')[1].text
                    enemy_numbers_match = re.search(r'\((\d+)\)', final_blow_info.text)
                    enemy_numbers = enemy_numbers_match.group(1) if enemy_numbers_match else ""

                    insert_data(system_name, victim_ship_type, victim_name, victim_corp, formatted_datetime,
                                enemy_player_name, enemy_corp_name, enemy_numbers)


# List of URLs
urls = [
    "https://zkillboard.com/ship/28659/losses/page/",
    "https://zkillboard.com/ship/28665/losses/page/",
    "https://zkillboard.com/ship/28710/losses/page/",
    "https://zkillboard.com/ship/33472/losses/page/",
    "https://zkillboard.com/ship/47271/losses/page",
    # Add more URLs here as needed
]

# Iterate through each URL
for base_url in urls:
    for page_num in range(1, 11):  # Pages 1 to 10
        url = f"{base_url}{page_num}/"
        print(f"Processing URL: {url}")
        process_url(url)  # Process the URL here (replace with your function)
        time.sleep(5)  # Pause for 30 seconds before the next iteration
        print(f"Success: Data from {url} inserted into the database.")

# Close the database connection
conn.close()
