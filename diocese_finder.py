from selenium import webdriver
import time
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == "__main__":
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Create a new Chrome driver instance.
    browser = webdriver.Chrome(options=chrome_options)

    # Construct URL by inserting the state name into the query string.
    base_url = "https://www.usccb.org/about/bishops-and-dioceses#tab--episcopal-regions-archdioceses-and-dioceses-in-the-us"

    url = f"{base_url}"
    
    # Initialize a new Chrome driver instance.
    browser.get(url)

    # Wait until the <td> elements containing "Diocese" are present.
    wait = WebDriverWait(browser, 10)
    diocese_elements = wait.until(
        EC.presence_of_all_elements_located(("xpath", "//*[contains(text(), 'Diocese') or contains(text(), 'Archdiocese') or contains(text(), 'Eparchy') or contains(text(), 'Archeparchy')]"))
    )


    # Extract the text from each element
    diocese_names = [elem.text for elem in diocese_elements]
    
    with open("all_diocese.csv", "w+") as file:
        for name in diocese_names:
            writer = file.writelines(name + "\n")

    browser.quit()
    