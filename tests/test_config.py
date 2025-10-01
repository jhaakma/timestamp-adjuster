#!/usr/bin/env python3
"""
Unit tests for configuration management functionality.
"""

import unittest
import tempfile
import os
from config import Config
from test_base import BaseTestCase


class TestConfiguration(BaseTestCase):
    """Test configuration management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call base class setUp
        self.config = self.get_test_config()
    
    def test_default_config(self):
        """Test default configuration values."""
        # Test default timestamp formats are loaded
        formats = self.config.get_timestamp_formats()
        self.assertIsInstance(formats, list)
        self.assertGreater(len(formats), 0)
        
        # Test that at least one format is enabled by default
        enabled_formats = [f for f in formats if f.get('enabled', True)]
        self.assertGreater(len(enabled_formats), 0)
    
    def test_config_file_loading(self):
        """Test loading configuration from YAML file."""
        # Create a temporary config file
        config_content = """
timestamp:
  input_formats:
    - pattern: "\\\\[(\\\\d{2}):(\\\\d{2}):(\\\\d{2})\\\\]"
      name: "test_format"
      groups: ["hours", "minutes", "seconds"]
      enabled: true

  output_format: "[{hours:02d}:{minutes:02d}:{seconds:02d}]"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_config_path = f.name
        
        # Register for cleanup
        self.register_test_file(temp_config_path)
        
        # Load config from temporary file
        config = Config(config_file=temp_config_path, test_mode=True)
        formats = config.get_timestamp_formats()
        
        # Verify the custom format was loaded
        self.assertEqual(len(formats), 1)
        self.assertEqual(formats[0]['name'], 'test_format')
        self.assertTrue(formats[0]['enabled'])
        
        # Verify output format
        self.assertEqual(config.get('timestamp.output_format'), '[{hours:02d}:{minutes:02d}:{seconds:02d}]')
    
    def test_enabled_flag_filtering(self):
        """Test that disabled formats are filtered out."""
        # Create config with mixed enabled/disabled formats
        config_content = """
timestamp:
  input_formats:
    - pattern: "\\\\[(\\\\d{2}):(\\\\d{2}):(\\\\d{2})\\\\]"
      name: "enabled_format"
      groups: ["hours", "minutes", "seconds"]
      enabled: true
    - pattern: "(\\\\d{2}):(\\\\d{2}):(\\\\d{2})"
      name: "disabled_format"
      groups: ["hours", "minutes", "seconds"]
      enabled: false
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            temp_config_path = f.name
        
        # Register for cleanup
        self.register_test_file(temp_config_path)
        
        config = Config(config_file=temp_config_path, test_mode=True)
        formats = config.get_timestamp_formats()
        
        # Should only return enabled formats
        self.assertEqual(len(formats), 1)
        self.assertEqual(formats[0]['name'], 'enabled_format')
    
    def test_environment_variable_override(self):
        """Test that environment variables override config values."""
        # Set environment variable
        os.environ['TIMESTAMP_FORMAT'] = '[ENV:{hours:02d}:{minutes:02d}:{seconds:02d}]'
        
        try:
            config = Config(ignore_user_config=True)
            template = config.get('timestamp.output_format', '{hours:02d}:{minutes:02d}:{seconds:02d}')
            self.assertEqual(template, '[ENV:{hours:02d}:{minutes:02d}:{seconds:02d}]')
        finally:
            # Clean up
            if 'TIMESTAMP_FORMAT' in os.environ:
                del os.environ['TIMESTAMP_FORMAT']


if __name__ == '__main__':
    unittest.main()
