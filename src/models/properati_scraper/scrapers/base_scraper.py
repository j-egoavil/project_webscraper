"""
Base scraper class with common functionality.
"""

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.helpers import human_pause, detect_captcha


class BaseScraper:
    """Base class for all scrapers with common functionality."""
    
    def __init__(self, driver):
        self.driver = driver

    def wait_for_page_load(self, timeout=15):
        """Wait for page to load completely."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        except Exception as e:
            logging.warning(f"⚠️ Timeout waiting for page: {e}")
            return False

    def scrape_with_captcha_protection(self, url, timeout=15):
        """
        Scrape URL with CAPTCHA protection.
        
        Args:
            url: URL to scrape
            timeout: Timeout for page load
        
        Returns:
            Page HTML or None if CAPTCHA detected
        """
        try:
            self.driver.get(url)
            if not self.wait_for_page_load(timeout):
                return None
                
            human_pause(1, 0.5)
            html = self.driver.page_source
            
            if detect_captcha(html):
                logging.warning(f"🚨 CAPTCHA detected at: {url}")
                return None
                
            return html
            
        except Exception as e:
            logging.warning(f"⚠️ Error loading page {url}: {e}")
            return None

    def scroll_page(self, scroll_pause=1.2, max_scrolls=6):
        """Scroll page to load dynamic content."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            human_pause(scroll_pause, 0)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height