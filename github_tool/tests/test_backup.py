import unittest
from unittest.mock import MagicMock, patch, mock_open
import tempfile
import shutil
import os
import json

# Import the functions you want to test from your script
from ..gh_backup import create_folder, backup_labels, backup_organization_resources

class TestBackupScript(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to use as the output directory for testing
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the temporary directory after testing
        shutil.rmtree(self.temp_dir)

    def test_create_folder(self):
        # Test if the create_folder function creates a directory
        test_dir = os.path.join(self.temp_dir, "test_folder")
        self.assertFalse(os.path.exists(test_dir))
        create_folder(test_dir)
        self.assertTrue(os.path.exists(test_dir))

if __name__ == "__main__":
    unittest.main()
