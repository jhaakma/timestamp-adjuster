#!/usr/bin/env python3
"""
Unit tests for timestamp adjustment functionality.
"""

import unittest
from main import adjust_timestamps
from config import Config


class TestTimestampAdjustment(unittest.TestCase):
    """Test timestamp adjustment functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
    
    def test_adjust_timestamps_positive(self):
        """Test adjusting timestamps with positive seconds."""
        text = "Line 1\n[00:01:30] Speaker: Hello\n[00:02:45] Speaker: World"
        result = adjust_timestamps(text, 30, self.config)
        self.assertIn("[00:02:00]", result)  # 00:01:30 + 30s
        self.assertIn("[00:03:15]", result)  # 00:02:45 + 30s
    
    def test_adjust_timestamps_negative(self):
        """Test adjusting timestamps with negative seconds."""
        text = "Line 1\n[00:03:30] Speaker: Hello\n[00:05:45] Speaker: World"
        result = adjust_timestamps(text, -90, self.config)  # -1 minute 30 seconds
        self.assertIn("[00:02:00]", result)  # 00:03:30 - 90s
        self.assertIn("[00:04:15]", result)  # 00:05:45 - 90s
    
    def test_adjust_timestamps_zero(self):
        """Test adjusting timestamps with zero seconds."""
        text = "Line 1\n[00:01:30] Speaker: Hello"
        result = adjust_timestamps(text, 0, self.config)
        self.assertIn("[00:01:30]", result)  # Should remain unchanged
    
    def test_adjust_timestamps_preserve_text(self):
        """Test that non-timestamp text is preserved."""
        text = "This is intro text\n[00:01:30] Speaker: Hello\nThis is outro text"
        result = adjust_timestamps(text, 30, self.config)
        self.assertIn("This is intro text", result)
        self.assertIn("Speaker: Hello", result)
        self.assertIn("This is outro text", result)
    
    def test_adjust_timestamps_no_timestamps(self):
        """Test adjusting text with no timestamps."""
        text = "This is just regular text\nwith no timestamps\nat all."
        result = adjust_timestamps(text, 30, self.config)
        self.assertEqual(result, text)  # Should be unchanged


if __name__ == '__main__':
    unittest.main()
