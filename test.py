from selenium import webdriver
import time
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed

def scrape_state(state):
    # Set Chrome options for headless mode.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # Create a new Chrome driver instance.
    browser = webdriver.Chrome(options=chrome_options)

    # Construct URL by inserting the state name into the query string.
    base_url = "https://www.catholicdirectory.com/united-states"

    url = f"{base_url}/{state}"
    
    # Initialize a new Chrome driver instance.
    browser.get(url)
    browser.maximize_window()

    time.sleep(1)
    # Now repeatedly click the "Load More" button.
    while True:
        try:
            old_count = len(browser.find_elements("css selector", "span.h3.bold.inline-block.member-search-full-name"))
            browser.execute_script(
                "document.body.scrollTop = document.body.scrollHeight; "
                "document.documentElement.scrollTop = document.documentElement.scrollHeight;"
            )

            # Wait for the "Load More" button to become clickable.
            element = WebDriverWait(browser, 20).until(EC.element_to_be_clickable(("css selector", ".btn.btn-primary.btn-block.btn-lg.bold.clickToLoadMoreBtn")))
            element.click()
            WebDriverWait(browser, 20).until(lambda b: len(b.find_elements("css selector", "span.h3.bold.inline-block.member-search-full-name")) > old_count)

            # Wait a bit for new results to load.
            browser.execute_script(
                "document.body.scrollTop = document.body.scrollHeight; "
                "document.documentElement.scrollTop = document.documentElement.scrollHeight;"
            )

        except Exception as e:
            break
    
    # Extract all church names
    church_names = []
    addresses = []
    try:
        church_elements = WebDriverWait(browser, 20).until(
            EC.presence_of_all_elements_located(("css selector", "span.h3.bold.inline-block.member-search-full-name"))
        )
        address_elements = WebDriverWait(browser, 20).until(
            EC.presence_of_all_elements_located(("css selector", "span.small.member-search-location.rmargin.rpad"))
        )
        for church in church_elements:
            church_names.append(church.text.strip())

        for address in address_elements:
            addresses.append(address.text.strip())

    except Exception as e:
        print(f"[{state}] Could not find church names: {e}")
    
    browser.quit()
    return {"State": state, "Num_Churches": len(church_names), "Church_Names": church_names, "Addresses" : addresses}


# # Page to search for ALL US Catholic churches. Make sure this is in SQUARE format for viewing parishes. NOT list format.
# browser.get("https://www.catholicdirectory.com/search_results?location_value=United+States&country_sn=US&location_type=country&stateSearch=&swlat=15.7760139&nelat=72.7087158&swlng=-173.2992296&nelng=-66.3193754&lat=38.7945952&lng=-106.5348379&faddress=United+States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&reviews&&name%20ASC&sort=")

# The website likely loads data dynamically using an API because it uses XHR and Fetch requests.
# Currently using selenium wire to give access to underlying requests made by the browser.

def save_state_data(state_data):
    """Save each state's church data into its own CSV file inside the 'states' folder."""
    state_filename = f"states/{state_data['State'].replace(' ', '_')}.csv"
    
    with open(state_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["State", "Num_Churches", "Church_Name", "Main Pastor Name", "Addresses", "Pastor's Phone Number", "Pastor's Email"])  # Initialize header
        
        # Ensure we're writing full names, not single characters
        for church, address in zip(state_data["Church_Names"], state_data["Addresses"]):
            writer.writerow([state_data["State"], state_data["Num_Churches"], church.strip(), "",  address, "", ""])  

def append_to_main_csv(state_data):
    """Append each state's data to a single main CSV file."""
    main_csv_filename = "churches_by_state.csv"
    
    with open(main_csv_filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Ensure full names are written, not single characters
        for church, address in zip(state_data["Church_Names"], state_data["Addresses"]):
            writer.writerow([state_data["State"], state_data["Num_Churches"], church.strip(), "",  address, "", ""])  

def only_states(state_data):
    """Append each state to a single main CSV file."""
    main_csv_filename = "only_states.csv"
    
    with open(main_csv_filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Ensure full names are written, not single characters
        writer.writerow([state_data["State"], state_data["Num_Churches"], state_data["Church_Names"], "", state_data["Addresses"], "", ""])

if __name__ == "__main__":
    start_time = time.perf_counter()
    # List of 50 US states.
    # states = [
    #    "Wyoming"
    # ]    
    states = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", 
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", 
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", 
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", 
        "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", 
        "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
    ]
    
    results = []

    # Initialize main CSV file before appending data
    main_csv_filename = "churches_by_state.csv"
    with open(main_csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["State", "Num_Churches", "Church_Name", "Main Pastor Name", "Addresses", "Pastor's Phone Number", "Pastor's Email"])  # Initialize header
    
    only_states_csv_filename = "only_states.csv"
    with open(only_states_csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["State", "Num_Churches", "Church_Name", "Main Pastor Name", "Addresses", "Pastor's Phone Number", "Pastor's Email"])  # Initialize header

    # Run all 50 states in parallel.
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(scrape_state, state): state for state in states}
        for future in as_completed(futures):
            state = futures[future]
            try:
                results = future.result()

                save_state_data(results)
                
                # Append to main CSV file
                append_to_main_csv(results)

                # Write to only_states.csv
                only_states(results)

            except Exception as exc:
                print(f"[{state}] Generated an exception: {exc}")

end_time = time.perf_counter()
execution_time = end_time - start_time

print(f"Execution time: {execution_time:.4f} seconds")

input("Press Enter to exit...")