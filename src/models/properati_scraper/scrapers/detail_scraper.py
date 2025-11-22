"""
Detail page scraper for individual properties.
"""

import logging
from datetime import datetime
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.helpers import safe_extract, extract_numeric_value, extract_business_type
from config import (
    TITLE_SELECTORS, PRICE_SELECTORS, LOCATION_SELECTORS,
    BEDROOM_KEYWORDS, BATHROOM_KEYWORDS, GARAGE_KEYWORDS, LOT_KEYWORDS
)


class DetailScraper(BaseScraper):
    """Scraper for individual property detail pages."""
    
    def _parse_detalle_html(self, html, url):
        """
        Parse individual property detail page.
        
        Args:
            html: Page HTML content
            url: Property URL
        
        Returns:
            Dictionary with property data
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Detect property type
        property_type = safe_extract(soup, [
            "[data-test='property-type-value']",
            ".property-type .place-features__values",
            ".property-type"
        ]).lower()
        
        # For lots and land, don't look for bedrooms/bathrooms
        is_lot_or_land = any(word in property_type for word in LOT_KEYWORDS)
        
        item = {
            "URL": url,
            "Title": safe_extract(soup, TITLE_SELECTORS),
            "Neighborhood": safe_extract(soup, LOCATION_SELECTORS),
            "Price": safe_extract(soup, PRICE_SELECTORS),
            "Built Area": safe_extract(soup, [
                "[data-test='floor-area-value']",
                ".floor-area .place-features__values",
                ".built-area",
                "[class*='area']"
            ]),
            "Land Area": safe_extract(soup, [
                "[data-test='plot-area-value']",
                "[data-test='area-value']",
                ".plot-area .place-features__values",
                ".land-area", 
                ".area-land"
            ]),
            "Bedrooms": "N/A" if is_lot_or_land else extract_numeric_value(
                soup, "bedrooms-value", BEDROOM_KEYWORDS
            ),
            "Bathrooms": "N/A" if is_lot_or_land else extract_numeric_value(
                soup, "full-bathrooms-value", BATHROOM_KEYWORDS
            ),
            "Garage": extract_numeric_value(soup, "parking-lots-value", GARAGE_KEYWORDS),
            "Stratum": safe_extract(soup, [
                "[data-test='stratum-value']",
                ".stratum .place-features__values",
                ".stratum",
                "[class*='stratum']"
            ]),
            "Year Built": safe_extract(soup, [
                "[data-test='construction-year-value']",
                ".year .place-features__values",
                ".year-built",
                ".construction-year",
                "[class*='year']"
            ]),
            "Administration Fee": safe_extract(soup, [
                "[data-test='community-price']",
                ".administration",
                ".admin-fee",
                "[class*='admin']"
            ]),
            "Property Type": safe_extract(soup, [
                "[data-test='property-type-value']",
                ".property-type .place-features__values",
                ".property-type",
                "[class*='type']"
            ]),
            "Business Type": extract_business_type(url, soup),
            "Status": "N/A",
            "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Error": None,
            "Property_Category": "Lote/Terreno" if is_lot_or_land else "Construcción"
        }

        return item

    def _parse_proyecto_html(self, html, url):
        """
        Parse project page (basic info).
        
        Args:
            html: Page HTML content
            url: Project URL
        
        Returns:
            Dictionary with project data
        """
        soup = BeautifulSoup(html, "html.parser")
        
        item = {
            "URL": url,
            "Title": safe_extract(soup, [
                "h1.header__text",
                "h1.title",
                ".project-title",
                "h1"
            ]),
            "Neighborhood": safe_extract(soup, [
                ".header__location span",
                ".location",
                ".project-location",
                ".address"
            ]),
            "Price": safe_extract(soup, [
                ".price-info__value",
                ".price",
                ".project-price",
                ".value"
            ]),
            "Built Area": "N/A",
            "Land Area": "N/A", 
            "Bedrooms": "N/A",
            "Bathrooms": "N/A",
            "Garage": "N/A",
            "Stratum": "N/A",
            "Year Built": "N/A",
            "Administration Fee": "N/A",
            "Property Type": "Proyecto",
            "Business Type": extract_business_type(url, soup),
            "Status": "N/A",
            "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Error": None,
            "Is_Project": "Sí"
        }

        return item

    def scrape_property(self, url):
        """
        Main method to scrape individual property.
        
        Args:
            url: Property URL
        
        Returns:
            Dictionary with property data
        """
        try:
            logging.info(f"🔍 Scraping property: {url}")
            html = self.scrape_with_captcha_protection(url)
            
            if html is None:
                return {
                    "URL": url,
                    "Error": "CAPTCHA detected",
                    "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            
            if "/proyecto/" in url:
                return self._parse_proyecto_html(html, url)
            elif "/detalle/" in url:
                return self._parse_detalle_html(html, url)
            else:
                return {"URL": url, "Error": "Unknown URL type"}
                
        except Exception as e:
            logging.error(f"❌ Error scraping property {url}: {e}")
            return {
                "URL": url, 
                "Error": f"scraping_error: {str(e)}",
                "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }