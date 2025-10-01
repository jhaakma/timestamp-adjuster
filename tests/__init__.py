"""
Test package for Timestamp Adjuster.
"""

import os
import sys

# Add the project root to the Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
