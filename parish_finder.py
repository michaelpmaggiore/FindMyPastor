from selenium import webdriver
import time
import csv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode

def scrape_state(state):
    # Set Chrome options for headless mode.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Create a new Chrome driver instance.
    browser = webdriver.Chrome(options=chrome_options)

    # Construct URL by inserting the state name into the query string.
    base_url = "https://www.catholicdirectory.com/search_results"
    params = {
        "q": state,
        "location_value": "USA",
        "country_sn": "US",
        "location_type": "country",
        "stateSearch": "",
        "swlat": "18.7763",
        "nelat": "74.071038",
        "swlng": "166.9999999",
        "nelng": "-66.885417",
        "lat": "38.7945952",
        "lng": "-106.5348379",
        "faddress": "United+States",
        "place_id": "ChIJCzYy5IS16lQRQrfeQ5K5Oxw"
    }
    url = f"{base_url}?{urlencode(params)}"
    # print(f"[{state}] Opening URL: {url}")
    
    # Initialize a new Chrome driver instance.
    browser.get(url)
    browser.maximize_window()
    # time.sleep(5)  # Allow the page to load

    actions = ActionChains(browser)

    # Click to switch to the grid view.
    # element = browser.find_element("css selector", ".fa.fa-th.js-click.gridView.hidden-xs")
    # element.click()
    time.sleep(1)
    # Now repeatedly click the "Load More" button.
    while True:
        try:
            # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            browser.execute_script("document.body.scrollTop = document.body.scrollHeight; document.documentElement.scrollTop = document.documentElement.scrollHeight;")
            # time.sleep(5)
            # Wait for the "Load More" button to become clickable.
            element = browser.find_element("css selector", ".btn.btn-primary.btn-block.btn-lg.bold.clickToLoadMoreBtn")
            element.click()
            # print("Clicked 'Load More' button, waiting for new results...")

            # Wait a bit for new results to load.
            time.sleep(5)
            browser.execute_script("document.body.scrollTop = document.body.scrollHeight; document.documentElement.scrollTop = document.documentElement.scrollHeight;")

            # print("Scrolled to top of the page.")
        except Exception as e:
            # print(f"[{state}] No more 'Load More' button found or clickable. Exiting loop. {e}")
            break
    
    # Extract all church names
    church_names = []
    try:
        church_elements = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located(("css selector", "span.h3.bold.inline-block.member-search-full-name"))
        )
        for church in church_elements:
            church_names.append(church.text.strip())  # Clean up text and add to list
        
        # print(f"[{state}] Found {len(church_names)} churches.")
    except Exception as e:
        print(f"[{state}] Could not find church names: {e}")
    
    browser.quit()
    # print(f"[{state}] Finished processing.")
    return {"State": state, "Num_Churches": len(church_names), "Church_Names": ", ".join(church_names)}

# browser = webdriver.Chrome()

# # Page to search for ALL US Catholic churches. Make sure this is in SQUARE format for viewing parishes. NOT list format.
# browser.get("https://www.catholicdirectory.com/search_results?location_value=United+States&country_sn=US&location_type=country&stateSearch=&swlat=15.7760139&nelat=72.7087158&swlng=-173.2992296&nelng=-66.3193754&lat=38.7945952&lng=-106.5348379&faddress=United+States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&reviews&&name%20ASC&sort=")

# The website likely loads data dynamically using an API because it uses XHR and Fetch requests.
# Currently using selenium wire to give access to underlying requests made by the browser.


# for _ in range(26):
#     actions.send_keys(Keys.TAB)
# actions.perform()

# # Now, get the element that currently has focus
# active_element = browser.switch_to.active_element

# # Extract its text or value depending on the element type
# if active_element.tag_name.lower() in ["input", "textarea"]:
#     text = active_element.get_attribute("value")
# else:
#     text = active_element.text

# with open ("csv", "w+") as file:
#     file.write(f"{text} \n")

#     for _ in range(3):
#         actions.send_keys(Keys.TAB)
#         actions.perform()
    
#     for i in range(300):
#         active_element = browser.switch_to.active_element
#         if active_element.tag_name.lower() in ["input", "textarea"]:
#             text = active_element.get_attribute("value")
#         else:
#             text = active_element.text
#         file.write(f"{text} \n")
#         actions.send_keys(Keys.TAB)
#         actions.perform()


if __name__ == "__main__":
    # List of 50 US states.
    states = [
        "Pennsylvania"
    ]
    # states = [
    #     "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
    #     "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", 
    #     "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", 
    #     "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", 
    #     "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", 
    #     "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", 
    #     "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
    # ]
    
    results = []
    
    # Run all 50 states in parallel.
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(scrape_state, state): state for state in states}
        for future in as_completed(futures):
            state = futures[future]
            try:
                results.append(future.result())
                # print(f"Completed: {result}")
            except Exception as exc:
                print(f"[{state}] Generated an exception: {exc}")

    # Write to CSV file
    csv_filename = "churches_by_state.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["State", "Num_Churches", "Church_Names"])
        writer.writeheader()
        writer.writerows(results)



# print("Copied text:", text)

input("Press Enter to exit...")