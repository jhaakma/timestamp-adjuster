#!/usr/bin/env python3
"""
Unit tests for file processing functionality.
"""

import unittest
import tempfile
import os
from main import process_file, generate_output_filename
from test_base import BaseTestCase


class TestFileProcessing(BaseTestCase):
    """Test file processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.config = self.get_test_config()
    
    def test_generate_output_filename_positive(self):
        """Test output filename generation with positive adjustment."""
        result = generate_output_filename("test.txt", 30, self.config)
        self.assertEqual(str(result), "outputs/test_plus30s.txt")
    
    def test_generate_output_filename_negative(self):
        """Test output filename generation with negative adjustment."""
        result = generate_output_filename("test.txt", -15, self.config)
        self.assertEqual(str(result), "outputs/test_minus15s.txt")
    
    def test_generate_output_filename_zero(self):
        """Test output filename generation with zero adjustment."""
        result = generate_output_filename("test.txt", 0, self.config)
        self.assertEqual(str(result), "outputs/test_plus0s.txt")
    
    def test_generate_output_filename_no_extension(self):
        """Test output filename generation without file extension."""
        result = generate_output_filename("test", 45, self.config)
        self.assertEqual(str(result), "outputs/test_plus45s")
    
    def test_process_file_with_timestamps(self):
        """Test processing file with timestamps."""
        # Create temporary input file
        input_content = """This is a test transcript.
[00:01:30] Speaker 1: Hello there.
[00:02:45] Speaker 2: How are you?
[00:03:15] Speaker 1: I'm doing well.
End of transcript."""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
            input_file.write(input_content)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as output_file:
            output_path = output_file.name
        
        # Register files for cleanup
        self.register_test_file(input_path)
        self.register_test_file(output_path)
        
        # Process the file with +30 seconds adjustment
        adjustment = 30
        process_file(input_path, output_path, adjustment, self.config)
        
        # Read the output file
        with open(output_path, 'r') as f:
            output_content = f.read()
        
        # Verify timestamps were adjusted
        self.assertIn("[00:02:00]", output_content)  # 00:01:30 + 30s
        self.assertIn("[00:03:15]", output_content)  # 00:02:45 + 30s
        self.assertIn("[00:03:45]", output_content)  # 00:03:15 + 30s
        
        # Verify non-timestamp content is preserved
        self.assertIn("This is a test transcript.", output_content)
        self.assertIn("Speaker 1: Hello there.", output_content)
        self.assertIn("End of transcript.", output_content)
    
    def test_process_file_no_timestamps(self):
        """Test processing file without timestamps."""
        # Create temporary input file without timestamps
        input_content = """This is a test file.
No timestamps here.
Just regular text."""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
            input_file.write(input_content)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as output_file:
            output_path = output_file.name
        
        # Register files for cleanup
        self.register_test_file(input_path)
        self.register_test_file(output_path)
        
        # Process the file
        process_file(input_path, output_path, 30, self.config)
        
        # Read the output file
        with open(output_path, 'r') as f:
            output_content = f.read()
        
        # Verify content is unchanged
        self.assertEqual(output_content.strip(), input_content.strip())


if __name__ == '__main__':
    unittest.main()
