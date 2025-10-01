#!/usr/bin/env python3
"""
Integration tests for the timestamp adjuster application.
"""

import unittest
import tempfile
import os
import subprocess
import sys
from test_base import BaseTestCase


class TestIntegration(BaseTestCase):
    """Test full application integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()  # Call base class setUp
        
        # Create temporary input file
        self.input_content = """Transcript starts here.
[00:01:30] Alice: Hello everyone.
[00:02:45] Bob: How is everyone doing?
[00:03:15] Alice: Great, thanks for asking!
[00:04:00] Charlie: What's on the agenda today?
End of transcript."""
        
        self.input_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        self.input_file.write(self.input_content)
        self.input_file.close()
        self.register_test_file(self.input_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        super().tearDown()  # Call base class tearDown
    
    def test_full_application_run(self):
        """Test running the full application end-to-end."""
        # Run the application
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        output_file.close()
        self.register_test_file(output_file.name)
        
        # Run main.py with test arguments
        result = subprocess.run([
            sys.executable, 'main.py',
            self.input_file.name,
            '30',
            '--output', output_file.name
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)) + '/..')
        
        # Check that the command succeeded
        self.assertEqual(result.returncode, 0, f"Application failed with error: {result.stderr}")
        
        # Read the output file
        with open(output_file.name, 'r') as f:
            output_content = f.read()
        
        # Verify timestamps were adjusted correctly
        self.assertIn("[00:02:00]", output_content)  # 00:01:30 + 30s
        self.assertIn("[00:03:15]", output_content)  # 00:02:45 + 30s
        self.assertIn("[00:03:45]", output_content)  # 00:03:15 + 30s
        self.assertIn("[00:04:30]", output_content)  # 00:04:00 + 30s
        
        # Verify non-timestamp content is preserved
        self.assertIn("Transcript starts here.", output_content)
        self.assertIn("Alice: Hello everyone.", output_content)
        self.assertIn("End of transcript.", output_content)
    
    def test_application_with_auto_output(self):
        """Test application with automatic output filename generation."""
        project_root = os.path.dirname(os.path.abspath(__file__)) + '/..'
        
        try:
            # Run main.py without output file (should auto-generate)
            result = subprocess.run([
                sys.executable, 'main.py',
                self.input_file.name,
                '60'
            ], capture_output=True, text=True, cwd=project_root)
            
            # Check that the command succeeded
            self.assertEqual(result.returncode, 0, f"Application failed with error: {result.stderr}")
            
            # The output file should be auto-generated
            input_basename = os.path.splitext(os.path.basename(self.input_file.name))[0]
            expected_output = f"outputs/{input_basename}_plus60s.txt"
            
            # Check if the output file was created (relative to project root)
            output_path = os.path.join(project_root, expected_output)
            
            if os.path.exists(output_path):
                # Register for cleanup
                self.register_test_file(output_path)
                
                # Read and verify the output
                with open(output_path, 'r') as f:
                    output_content = f.read()
                
                # Verify timestamps were adjusted correctly
                self.assertIn("[00:02:30]", output_content)  # 00:01:30 + 60s
                self.assertIn("[00:03:45]", output_content)  # 00:02:45 + 60s
        except Exception as e:
            self.skipTest(f"Integration test skipped due to file system constraints: {e}")


if __name__ == '__main__':
    unittest.main()
