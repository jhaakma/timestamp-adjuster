#!/usr/bin/env python3
"""
Base test class with cleanup functionality for test-generated files.
"""

import unittest
import os
import glob
from pathlib import Path
from config import Config


class BaseTestCase(unittest.TestCase):
    """Base test case with cleanup functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - record existing files."""
        cls.project_root = Path(__file__).parent.parent
        cls.outputs_dir = cls.project_root / "outputs"
        cls.initial_output_files = set()
        
        # Record files that existed before tests
        if cls.outputs_dir.exists():
            cls.initial_output_files = set(f.name for f in cls.outputs_dir.iterdir() if f.is_file())
    
    def get_test_config(self, config_file=None):
        """Get a configuration object for testing that ignores user config."""
        return Config(config_file=config_file, ignore_user_config=True)
    
    def setUp(self):
        """Set up individual test - record current state."""
        self.test_generated_files = []
    
    def tearDown(self):
        """Clean up individual test - remove any files this test generated."""
        # Clean up any files specifically tracked by this test
        for file_path in self.test_generated_files:
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except (OSError, PermissionError):
                    pass  # Ignore cleanup errors
        
        # Clean up any temporary files in outputs directory
        self._cleanup_test_outputs()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test class - remove any remaining test files."""
        if cls.outputs_dir.exists():
            current_files = set(f.name for f in cls.outputs_dir.iterdir() if f.is_file())
            new_files = current_files - cls.initial_output_files
            
            for filename in new_files:
                file_path = cls.outputs_dir / filename
                try:
                    file_path.unlink()
                except (OSError, PermissionError):
                    pass  # Ignore cleanup errors
    
    def _cleanup_test_outputs(self):
        """Clean up test-generated files in outputs directory."""
        if not self.outputs_dir.exists():
            return
        
        # Patterns for test-generated files
        test_patterns = [
            "tmp*",  # Temporary files
            "*_plus*s.*",  # Files with adjustment patterns
            "*_minus*s.*",  # Files with adjustment patterns
        ]
        
        for pattern in test_patterns:
            for file_path in self.outputs_dir.glob(pattern):
                # Only clean files that are likely test-generated
                # Check if file was created recently (within last 5 minutes)
                try:
                    stat = file_path.stat()
                    import time
                    if time.time() - stat.st_mtime < 300:  # 5 minutes
                        file_path.unlink()
                except (OSError, PermissionError):
                    pass  # Ignore cleanup errors
    
    def register_test_file(self, file_path):
        """Register a file for cleanup after the test."""
        self.test_generated_files.append(str(file_path))
