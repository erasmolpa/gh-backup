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

    @patch("github.Repository")
    def test_backup_labels(self, mock_repository):
        # Test the backup_labels function
        repo = mock_repository()
        repo.get_labels.return_value = [MagicMock(name="label1", color="red")]

        repo_folder = os.path.join(self.temp_dir, "test_repo")
        create_folder(repo_folder)

        backup_labels(repo, repo_folder)

        labels_file_path = os.path.join(repo_folder, "labels.json")
        self.assertTrue(os.path.exists(labels_file_path))
        with open(labels_file_path, "r") as labels_file:
            labels_data = json.load(labels_file)
            self.assertEqual(labels_data, [{"name": "label1", "color": "red"}])
            
    @patch('your_backup_script.Github')
    @patch('builtins.open', mock_open())
    @patch('os.makedirs')
    def test_backup_organization_resources(self, mock_os_makedirs, mock_github):
        org_name = 'test_org'
        access_token = 'test_token'
        output_dir = self.temp_dir
        repo_names = ['repo1', 'repo2']

        # Mock the Github library
        mock_repo1 = MagicMock(name='repo1', clone_url='https://github.com/org/repo1.git')
        mock_repo2 = MagicMock(name='repo2', clone_url='https://github.com/org/repo2.git')
        mock_org = MagicMock(name='org')
        mock_org.get_repos.return_value = [mock_repo1, mock_repo2]

        # Mock the Github object
        mock_github.return_value.get_organization.return_value = mock_org

        # Call the function to be tested
        backup_organization_resources(org_name, access_token, output_dir, repo_names)

        # Assertions
        mock_os_makedirs.assert_called_once_with(os.path.join(output_dir, org_name), exist_ok=True)
        mock_github.assert_called_once_with(access_token)
        mock_github.return_value.get_organization.assert_called_once_with(org_name)
        mock_github.return_value.get_organization.return_value.get_repos.assert_called_once_with()
        
        # Verify that the JSON file was written correctly
        with open(os.path.join(output_dir, org_name, 'organization.json')) as org_file:
            org_data = json.load(org_file)
            self.assertEqual(org_data['name'], org_name)
            self.assertEqual(org_data['repositories'], repo_names)
            
        # Verify that the repositories were backed up
        self.assertTrue(os.path.exists(os.path.join(output_dir, org_name, 'repo1')))
        self.assertTrue(os.path.exists(os.path.join(output_dir, org_name, 'repo2')))


if __name__ == "__main__":
    unittest.main()
