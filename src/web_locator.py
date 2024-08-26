import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from enum import Enum
from functools import wraps
from contextlib import contextmanager
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LocatorType(Enum):
    ID = By.ID
    XPATH = By.XPATH
    CSS = By.CSS_SELECTOR
    CLASS_NAME = By.CLASS_NAME

@contextmanager
def webdriver_context(incognito=False):
    options = webdriver.ChromeOptions()
    if incognito:
        options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()

def retry(retries=3, exceptions=(StaleElementReferenceException, TimeoutException)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logging.warning(f"{type(e).__name__} occurred. Retrying... ({attempt + 1}/{retries})")
                except Exception as e:
                    logging.error(f"Unhandled exception in {func.__name__}: {e}")
                    break
            logging.error(f"Max retries exceeded for {func.__name__}")
            return None
        return wrapper
    return decorator

class WebElementLocator:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def _get_by_type(self, locator_type: LocatorType):
        if not isinstance(locator_type, LocatorType):
            raise ValueError(f"Invalid locator type: {locator_type}")
        return locator_type.value

    @retry()
    def wait_for_elements(self, locator_type: LocatorType, locator_value: str, timeout=10):
        by = self._get_by_type(locator_type)
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, locator_value))
            )
            logging.info(f"Found {len(elements)} elements with {locator_type.name}='{locator_value}'")
            return elements
        except TimeoutException:
            logging.error(f"Timeout waiting for elements with {locator_type.name}='{locator_value}'")
            return []

    @retry()
    def find_element_relative_to(self, element, relative_locator_type: LocatorType, relative_locator_value: str, timeout=5):
        by = self._get_by_type(relative_locator_type)
        return WebDriverWait(element, timeout).until(
            EC.presence_of_element_located((by, relative_locator_value))
        )

    def count_elements(self, locator_type: LocatorType, locator_value: str) -> int:
        by = self._get_by_type(locator_type)
        try:
            elements = self.driver.find_elements(by, locator_value)
            return len(elements)
        except Exception as e:
            logging.error(f"Error counting elements: {e}")
            return 0

    def start(self, url: str):
        try:
            self.driver.get(url)
            logging.info(f"Navigated to {url}")
        except Exception as e:
            logging.error(f"Error navigating to {url}: {e}")

    def get_target_and_siblings(self, target_locator: tuple, sibling_locator: tuple):
        target_element = self.wait_for_elements(*target_locator)
        if not target_element:
            return None

        sibling_elements = []
        if sibling_locator:
            try:
                sibling_elements = target_element[0].find_elements(*sibling_locator)
            except Exception as e:
                logging.error(f"Error finding sibling elements: {e}")
                return None

        return target_element[0], sibling_elements

    def get_html_content(self, elements):
        return [element.get_attribute('outerHTML') for element in elements]

def click_element(self, element, timeout=10):
    def _click_with_retry(click_func):
        for attempt in range(3):
            try:
                click_func()
                logging.info("Clicked element successfully")
                return True
            except ElementClickInterceptedException as e:
                logging.warning(f"ElementClickInterceptedException: {e}. Retrying... ({attempt + 1}/3)")
                # Optionally scroll the element into view again or take another action
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)  # Small delay to allow any animations to finish
            except Exception as e:
                logging.error(f"Unhandled exception during click: {e}")
                break
        return False

    try:
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(element))
    except TimeoutException:
        logging.error("Timeout waiting for element to be clickable")
        return False

    # Try scrolling into view and regular click
    self.driver.execute_script("arguments[0].scrollIntoView();", element)
    if _click_with_retry(element.click):
        return True

    # Try JavaScript click as a fallback
    if _click_with_retry(lambda: self.driver.execute_script("arguments[0].click();", element)):
        return True

    logging.error("Failed to click element even after retries and using JavaScript")
    return False
