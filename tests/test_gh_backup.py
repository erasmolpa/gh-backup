import unittest
from unittest.mock import Mock, patch
import tempfile
import os
import json

from ..gh_backup import create_folder, backup_labels, backup_issues, backup_repository, backup_organization_resources

class TestGithubBackup(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch('os.makedirs')
    def test_create_folder(self, mock_makedirs):
        path = os.path.join(self.temp_dir.name, 'test_folder')
        create_folder(path)
        mock_makedirs.assert_called_with(path, exist_ok=True)

    @patch('github.Repository.get_labels')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_backup_labels(self, mock_open, mock_get_labels):
        repo_folder = os.path.join(self.temp_dir.name, 'test_repo')
        repo = Mock()
        label1 = Mock(name='label1', color='red')
        label2 = Mock(name='label2', color='blue')
        labels = [label1, label2]
        mock_get_labels.return_value = labels

        backup_labels(repo, repo_folder)

        mock_get_labels.assert_called_once()
        mock_open.assert_called_once_with(os.path.join(repo_folder, 'labels.json'), 'w')
        handle = mock_open()
        handle.write.assert_called_once()

        # Verify that the content written to the file is as expected
        expected_content = json.dumps([{"name": 'label1', "color": 'red'}, {"name": 'label2', "color": 'blue'}], indent=4)
        handle.write.assert_called_with(expected_content)

    @patch('github.Repository.get_issues')
    @patch('github.Issue.get_labels')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_backup_issues(self, mock_open, mock_get_labels, mock_get_issues):
        repo_folder = os.path.join(self.temp_dir.name, 'test_repo')
        repo = Mock()
        issue1 = Mock(number=1, title='Issue 1', body='Body 1', state='open', created_at='2023-11-03T12:00:00Z', updated_at='2023-11-04T12:00:00Z', closed_at=None, user=Mock(login='user1'), get_labels=Mock(return_value=[Mock(name='label1')]))

        issue2 = Mock(number=2, title='Issue 2', body='Body 2', state='closed', created_at='2023-11-05T12:00:00Z', updated_at='2023-11-06T12:00:00Z', closed_at='2023-11-07T12:00:00Z', user=Mock(login='user2'), get_labels=Mock(return_value=[Mock(name='label2')]))

        issues = [issue1, issue2]
        mock_get_issues.return_value = issues

        backup_issues(repo, repo_folder)

        mock_get_issues.assert_called_once()
        mock_open.assert_called_once_with(os.path.join(repo_folder, 'issues.json'), 'w')
        handle = mock_open()
        handle.write.assert_called_once()

        # Verify that the content written to the file is as expected
        expected_content = json.dumps([
            {
                "number": 1,
                "title": "Issue 1",
                "body": "Body 1",
                "state": "open",
                "created_at": "2023-11-03T12:00:00Z",
                "updated_at": "2023-11-04T12:00:00Z",
                "closed_at": None,
                "user": "user1",
                "labels": ["label1"]
            },
            {
                "number": 2,
                "title": "Issue 2",
                "body": "Body 2",
                "state": "closed",
                "created_at": "2023-11-05T12:00:00Z",
                "updated_at": "2023-11-06T12:00:00Z",
                "closed_at": "2023-11-07T12:00:00Z",
                "user": "user2",
                "labels": ["label2"]
            }
        ], indent=4)
        handle.write.assert_called_with(expected_content)

    @patch('os.makedirs')
    @patch('github.Repository.get_labels')
    @patch('github.Repository.get_issues')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_backup_repository(self, mock_open, mock_get_issues, mock_get_labels, mock_makedirs):
        repo_folder = os.path.join(self.temp_dir.name, 'test_repo')
        org_folder = self.temp_dir.name
        repo = Mock(name='test_repo', description='Test repo', homepage='https://test.com', language='Python', created_at='2023-11-03T12:00:00Z', updated_at='2023-11-04T12:00:00Z')

        label1 = Mock(name='label1', color='red')
        label2 = Mock(name='label2', color='blue')
        labels = [label1, label2]
        mock_get_labels.return_value = labels

        issue1 = Mock(number=1, title='Issue 1', body='Body 1', state='open', created_at='2023-11-03T12:00:00Z', updated_at='2023-11-04T12:00:00Z', closed_at=None, user=Mock(login='user1'), get_labels=Mock(return_value=[Mock(name='label1')]))

        issue2 = Mock(number=2, title='Issue 2', body='Body 2', state='closed', created_at='2023-11-05T12:00:00Z', updated_at='2023-11-06T12:00:00Z', closed_at='2023-11-07T12:00:00Z', user=Mock(login='user2'), get_labels=Mock(return_value=[Mock(name='label2')]))

        issues = [issue1, issue2]
        mock_get_issues.return_value = issues

        backup_repository(repo, org_folder)

        mock_get_labels.assert_called_once()
        mock_get_issues.assert_called_once()
        mock_open.assert_called_with(os.path.join(repo_folder, 'repository.json'), 'w')
        handle = mock_open()
        handle.write.assert_called_once()

        # Verify that the content written to the file is as expected
        expected_content = json.dumps({
            "name": "test_repo",
            "description": "Test repo",
            "website": "https://test.com",
            "language": "Python",
            "created_at": "2023-11-03T12:00:00Z",
            "updated_at": "2023-11-04T12:00:00Z"})
       
