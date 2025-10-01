#!/usr/bin/env python3
"""
Unit tests for timestamp parsing functionality.
"""

import unittest
from main import parse_timestamp


class TestTimestampParsing(unittest.TestCase):
    """Test timestamp parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formats = [
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
                "enabled": True
            }
        ]
    
    def test_parse_bracketed_timestamp(self):
        """Test parsing [HH:MM:SS] format."""
        result = parse_timestamp("[01:30:45]", self.formats)
        expected = 1 * 3600 + 30 * 60 + 45  # 5445 seconds
        self.assertEqual(result, expected)
    
    def test_parse_simple_timestamp(self):
        """Test parsing HH:MM:SS format."""
        result = parse_timestamp("02:15:30", self.formats)
        expected = 2 * 3600 + 15 * 60 + 30  # 8130 seconds
        self.assertEqual(result, expected)
    
    def test_parse_flexible_timestamp(self):
        """Test parsing [H:MM:SS] format."""
        result = parse_timestamp("[3:45:20]", self.formats)
        expected = 3 * 3600 + 45 * 60 + 20  # 13520 seconds
        self.assertEqual(result, expected)
    
    def test_parse_invalid_timestamp(self):
        """Test parsing invalid timestamp format."""
        result = parse_timestamp("invalid", self.formats)
        self.assertIsNone(result)
    
    def test_parse_with_disabled_format(self):
        """Test that disabled formats are not parsed."""
        disabled_formats = [
            {
                "pattern": r'\[(\d{2}):(\d{2}):(\d{2})\]',
                "name": "bracketed_hms",
                "groups": ["hours", "minutes", "seconds"],
                "enabled": False
            }
        ]
        result = parse_timestamp("[01:30:45]", disabled_formats)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
