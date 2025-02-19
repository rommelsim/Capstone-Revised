from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import time

from robot.api.deco import keyword

CHROME_DRIVER_PATH = r".\chromedriver.exe"
REMOTE_DEBUGGING_PORT = 9229        # Synapse default port, don't modify.

# Ensure that Synapse is running in the background before doing anything...
class SynapseWebDriverClass:
    def __init__(self):
        
        try: 
            # Tab Name
            self.tab:str = ""

            # Define options for webdriver...
            self.options = Options()
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--headless")
            self.options.add_argument('--start-maximized')
            self.options.add_argument("--disable-dev-shm-usage")
            self.options.add_argument("--web-log-stream-to-console")
            self.options.add_argument("--hibernate-timeout=999999999")
            self.options.add_argument("--log-level=3")
            self.options.add_argument("--disable-background-timer-throttling")
            self.options.add_experimental_option("debuggerAddress", "localhost:" + str(REMOTE_DEBUGGING_PORT))

            # Define service...
            self.service = Service(executable_path=CHROME_DRIVER_PATH)

            # Define driver...
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
            print("SYNAPSE ATTACHED: PASS")
        except Exception as e:
            print(f"Error: {e}")
    
    def getDriver(self)->WebDriver:
        return self.driver

    @keyword("SwitchSynapseTabTo")
    def switchSynapseTabTo(self, tab_name):
        elems = self.driver.find_elements(By.CSS_SELECTOR, "*")
        for index, element in enumerate(elems):
            if element.text == tab_name:
                try:
                    self.tab = tab_name
                    element.click()
                    break
                except:
                    print(f"Cannot find element: {tab_name}. Exiting")

    @keyword("ClickOnElement")
    def clickOnElement(self, elem_name):
        driver = self.driver
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if driver.title == self.tab:
                driver.find_element(By.CSS_SELECTOR, elem_name).click()