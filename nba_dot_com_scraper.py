from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


# get base url
url = "https://www.nba.com/stats/players/advanced?SeasonType=Regular+Season&Season=2022-23"

# set up the driver
service = Service(executable_path=GeckoDriverManager().install())
# Configure Firefox options
options = Options()
# If running selenium locally toggling headless off can help to visualise the spider's actions
options.add_argument("--headless")
options.add_argument(
    "--disable-blink-features=AutomationControlled"
)  # To avoid getting detected
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
driver = webdriver.Firefox(service=service, options=options)

# get the advanced stats page
driver.get(url)

# Wait for the obstructing element to disappear
WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.ID, "onetrust-button-group"))
)

WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.ID, "onetrust-reject-all-handler"))
)


# click the option value -1
xpath = "//div[contains(@class, 'Pagination_pageDropdown')]"
option = driver.find_element(By.XPATH, xpath)
# click option
option.click()
print("click")
# then click the "-1" option
xpath = "//*[@value='-1']"
option = option.find_element(By.XPATH, xpath)
option.click()
print("click")

# now parse out the table
table_xp = "//table[@class='Crom_table__p1iZz']"
table = driver.find_element(By.XPATH, table_xp)

# find the headers
header_xp = "//thead/tr/th/@field"
headers = WebDriverWait(table, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, header_xp))
)
# Extract the text content from each 'th' element
header_texts = [header.text for header in headers]
print(header_texts)
