import requests
from bs4 import BeautifulSoup
import csv
# Base URL of the first page
base_url = "https://www.shl.com/solutions/products/product-catalog/"

page = 1  # Start from page 1
all_data = []

while True:
    url = base_url.format(page)
    print(f"Scraping: {url}")

    # Fetch the page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table
    table = soup.find("table")
    if not table:
        print("No more pages.")
        break  # Exit loop when no table is found

    # Extract rows
    for row in table.find_all("tr")[1:]:  # Skip header
        cols = row.find_all("td")
        if len(cols) < 4:
            continue  # Skip invalid rows

        name_tag = cols[0].find("a")
        assessment_name = name_tag.text.strip() if name_tag else cols[0].get_text(strip=True)
        assessment_url = name_tag["href"] if name_tag else "N/A"

        if assessment_url.startswith("/"):
            assessment_url = f"https://www.shl.com/{assessment_url}" 
            print(assessment_url) # Change domain accordingly

        remote_testing = "✔" if "●" in cols[1].text else "✖"
        adaptive_irt = "✔" if "●" in cols[2].text else "✖"
        test_types = ", ".join([t.text for t in cols[3].find_all("span")])

        all_data.append([assessment_name, assessment_url, remote_testing, adaptive_irt, test_types])

    # Check if there's a "Next" button
    next_button = soup.find("a", text="Next")  # Update selector based on website
    if not next_button:
        break  # No more pages

    page += 1  # Move to the next page

# Save data to CSV
csv_filename = "shl_req.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Assessment Name", "Assessment URL", "Remote Testing", "Adaptive/IRT", "Test Types"])  # Header
    writer.writerows(all_data)  # Data rows

print(f"Data saved successfully to {csv_filename}")
