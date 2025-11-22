"""
File handling utilities for data storage.
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime

from config import DATA_FOLDER


class DataHandler:
    """Handle data storage in CSV and JSON formats."""
    
    def __init__(self):
        self.csv_filename = None
        self.json_filename = None
        self._initialize_filenames()

    def _initialize_filenames(self):
        """Initialize unique filenames for this execution."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_filename = os.path.join(DATA_FOLDER, f"properati_data_{timestamp}.csv")
        self.json_filename = os.path.join(DATA_FOLDER, f"properati_data_{timestamp}.json")
        logging.info(f"📁 Data files: {self.csv_filename}")

    def save_data(self, data, force_save=False):
        """
        Save data to CSV and JSON files.
        
        Args:
            data: List of property dictionaries
            force_save: Whether to force save regardless of interval
        """
        if not data:
            return
            
        try:
            # Save CSV
            df = pd.DataFrame(data)
            df.to_csv(self.csv_filename, index=False, encoding="utf-8-sig")
            
            # Save JSON
            with open(self.json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"💾 Data saved: {len(data)} properties")
            logging.info(f"   📄 CSV: {self.csv_filename}")
            logging.info(f"   📋 JSON: {self.json_filename}")
            
        except Exception as e:
            logging.error(f"❌ Error saving data: {e}")

    def generate_statistics(self, data):
        """
        Generate statistics from scraped data.
        
        Args:
            data: List of property dictionaries
        
        Returns:
            Dictionary with statistics
        """
        valid_data = [item for item in data if item.get('Title') != 'N/A' and not item.get('Error')]
        projects = [item for item in data if item.get('Is_Project') == 'Sí']
        project_units = [item for item in data if item.get('Is_Project_Unit') == 'Sí']
        lots = [item for item in data if item.get('Property_Category') == 'Lote/Terreno']
        
        stats = {
            'total_records': len(data),
            'valid_records': len(valid_data),
            'projects': len(projects),
            'project_units': len(project_units),
            'individual_properties': len(valid_data) - len(projects) - len(project_units),
            'lots_land': len(lots)
        }
        
        return stats

    def log_statistics(self, data):
        """Log statistics about scraped data."""
        stats = self.generate_statistics(data)
        
        logging.info("📊 Final summary:")
        logging.info(f"   📈 Total records: {stats['total_records']}")
        logging.info(f"   ✅ Valid: {stats['valid_records']}")
        logging.info(f"   🏗️ Projects: {stats['projects']}")
        logging.info(f"   🏠 Project units: {stats['project_units']}")
        logging.info(f"   🏡 Individual properties: {stats['individual_properties']}")
        logging.info(f"   🏞️ Lots/Land: {stats['lots_land']}")