#!/usr/bin/env python3
"""
Unit tests for timestamp formatting functionality.
"""

import unittest
from main import seconds_to_timestamp


class TestTimestampFormatting(unittest.TestCase):
    """Test timestamp formatting functionality."""
    
    def test_format_timestamp_default(self):
        """Test default timestamp formatting."""
        seconds = 3661  # 1 hour, 1 minute, 1 second
        result = seconds_to_timestamp(seconds, "{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.assertEqual(result, "01:01:01")
    
    def test_format_timestamp_custom_template(self):
        """Test custom timestamp formatting."""
        seconds = 3661  # 1 hour, 1 minute, 1 second
        template = "[{hours:02d}:{minutes:02d}:{seconds:02d}]"
        result = seconds_to_timestamp(seconds, template)
        self.assertEqual(result, "[01:01:01]")
    
    def test_format_zero_seconds(self):
        """Test formatting zero seconds."""
        result = seconds_to_timestamp(0, "{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.assertEqual(result, "00:00:00")
    
    def test_format_large_timestamp(self):
        """Test formatting large timestamp."""
        seconds = 7323  # 2 hours, 2 minutes, 3 seconds
        result = seconds_to_timestamp(seconds, "{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.assertEqual(result, "02:02:03")


if __name__ == '__main__':
    unittest.main()
