#!/usr/bin/env python3
"""
Configuration management for Timestamp Adjuster.
Handles loading configuration from YAML files, environment variables, and defaults.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class Config:
    """Configuration manager for timestamp adjuster."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to config file. If None, uses default locations.
        """
        self.config_data = {}
        self.load_config(config_file)
    
    def load_config(self, config_file: Optional[str] = None):
        """
        Load configuration from file, environment variables, and defaults.
        Priority: Environment vars > Config file > Defaults
        """
        # Start with defaults
        self.config_data = self._get_defaults()
        
        # Load from config file
        config_path = self._find_config_file(config_file)
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}
                self._merge_config(self.config_data, file_config)
                print(f"Loaded configuration from: {config_path}")
            except Exception as e:
                print(f"Warning: Could not load config file {config_path}: {e}")
        
        # Override with environment variables
        self._load_env_vars()
    
    def _find_config_file(self, config_file: Optional[str] = None) -> Optional[Path]:
        """Find configuration file in order of preference."""
        if config_file:
            return Path(config_file)
        
        # Check in order of preference
        possible_locations = [
            Path("config.yaml"),  # Current directory
            Path("timestamp-adjuster.yaml"),  # Current directory alternative
            Path.home() / ".config" / "timestamp-adjuster" / "config.yaml",  # User config dir
            Path.home() / ".timestamp-adjuster.yaml",  # User home dir
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        
        return None
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "timestamp": {
                "input_formats": [
                    {
                        "pattern": r'\[(\d{2}):(\d{2}):(\d{2})\]',
                        "name": "bracketed_hms",
                        "groups": ["hours", "minutes", "seconds"],
                        "enabled": True
                    },
                    {
                        "pattern": r'(\d{2}):(\d{2}):(\d{2})',
                        "name": "simple_hms", 
                        "groups": ["hours", "minutes", "seconds"],
                        "enabled": True
                    },
                    {
                        "pattern": r'\[(\d{1,2}):(\d{2}):(\d{2})\]',
                        "name": "bracketed_hms_flex",
                        "groups": ["hours", "minutes", "seconds"],
                        "enabled": False
                    }
                ],
                "output_format": "[{hours:02d}:{minutes:02d}:{seconds:02d}]",
                "default_format": "bracketed_hms"
            },
            "files": {
                "input_dir": "inputs",
                "output_dir": "outputs", 
                "encoding": "utf-8",
                "create_backup": False
            },
            "output_naming": {
                "template": "{basename}_{sign}{adjustment}s{extension}",
                "positive_sign": "plus",
                "negative_sign": "minus"
            },
            "processing": {
                "negative_handling": "zero",
                "preserve_formatting": True
            }
        }
    
    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Timestamp format override
        if env_format := os.getenv("TIMESTAMP_FORMAT"):
            self.config_data["timestamp"]["output_format"] = env_format
        
        # Input/output directories
        if env_input_dir := os.getenv("TIMESTAMP_INPUT_DIR"):
            self.config_data["files"]["input_dir"] = env_input_dir
            
        if env_output_dir := os.getenv("TIMESTAMP_OUTPUT_DIR"):
            self.config_data["files"]["output_dir"] = env_output_dir
        
        # File encoding
        if env_encoding := os.getenv("TIMESTAMP_ENCODING"):
            self.config_data["files"]["encoding"] = env_encoding
    
    def get(self, key_path: str, default=None):
        """
        Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path like "timestamp.output_format"
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_timestamp_formats(self) -> List[Dict[str, Any]]:
        """Get list of enabled timestamp input formats."""
        all_formats = self.get("timestamp.input_formats", [])
        # Filter to only return enabled formats
        enabled_formats = [fmt for fmt in all_formats if fmt.get("enabled", True)]
        return enabled_formats
    
    def get_all_timestamp_formats(self) -> List[Dict[str, Any]]:
        """Get list of all timestamp input formats (including disabled ones)."""
        return self.get("timestamp.input_formats", [])
    
    def get_output_format(self) -> str:
        """Get timestamp output format template."""
        return self.get("timestamp.output_format", "[{hours:02d}:{minutes:02d}:{seconds:02d}]")
    
    def get_input_dir(self) -> str:
        """Get default input directory."""
        return self.get("files.input_dir", "inputs")
    
    def get_output_dir(self) -> str:
        """Get default output directory."""
        return self.get("files.output_dir", "outputs")
    
    def get_encoding(self) -> str:
        """Get file encoding."""
        return self.get("files.encoding", "utf-8")
    
    def get_output_template(self) -> str:
        """Get output filename template."""
        return self.get("output_naming.template", "{basename}_{sign}{adjustment}s{extension}")
    
    def get_positive_sign(self) -> str:
        """Get positive adjustment sign."""
        return self.get("output_naming.positive_sign", "plus")
    
    def get_negative_sign(self) -> str:
        """Get negative adjustment sign."""
        return self.get("output_naming.negative_sign", "minus")


# Global config instance
_config_instance = None

def get_config(config_file: Optional[str] = None) -> Config:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None or config_file is not None:
        _config_instance = Config(config_file)
    return _config_instance
