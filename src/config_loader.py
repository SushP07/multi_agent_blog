import json
import os
from typing import Dict

class ConfigLoader:
    def __init__(self, config_path: str = "config/sources.json"):
        self.config_path = config_path

    def load_sources(self) -> Dict[str, str]:
        """Loads and validates the news source channels from the JSON config."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file missing at: {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in configuration file: {e}")