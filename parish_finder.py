from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()

# Page to search for ALL US Catholic churches. Make sure this is in SQUARE format for viewing parishes. NOT list format.
browser.get("https://www.catholicdirectory.com/search_results?location_value=United+States&country_sn=US&location_type=country&stateSearch=&swlat=15.7760139&nelat=72.7087158&swlng=-173.2992296&nelng=-66.3193754&lat=38.7945952&lng=-106.5348379&faddress=United+States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&reviews&&name%20ASC&sort=")

# The website likely loads data dynamically using an API because it uses XHR and Fetch requests.
# Currently using selenium wire to give access to underlying requests made by the browser.

# Use ActionChains to send 34 TAB key presses
actions = ActionChains(browser)

# Click to switch to the grid view.
element = browser.find_element("css selector", ".fa.fa-th.js-click.gridView.hidden-xs")
element.click()
time.sleep(1)
# Now repeatedly click the "Load More" button.
while True:
    try:
        # Wait for the "Load More" button to become clickable.
        element = browser.find_element("css selector", ".btn.btn-primary.btn-block.btn-lg.bold.clickToLoadMoreBtn")
        element.click()
        print("Clicked 'Load More' button, waiting for new results...")

        # Wait a bit for new results to load.
        time.sleep(4)
        browser.execute_script("window.scrollTo(0, 0);")
        print("Scrolled to top of the page.")
    except Exception as e:
        print("No more 'Load More' button found or clickable. Exiting loop.")
        break

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






# print("Copied text:", text)

input("Press Enter to exit...")
browser.quit()
