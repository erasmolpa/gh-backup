import json
import argparse
import os
import logging
import zipfile
import shutil
import git 
from git import Repo, GitCommandError

from datetime import datetime
from github import Github

global org_name
global access_token 
global backup_zip_path


def restore_git_repository(repo_restored_name, local_repo_path, token):
    try:
        logging.info(f"Parameters: repo_restored_name={repo_restored_name}, local_repo_path={local_repo_path}")

        if not os.path.exists(local_repo_path):
            logging.error(f"Local repository folder does not exist: {local_repo_path}")
            return

        git_folder = find_git_folder(local_repo_path)
        if not git_folder:
            raise RuntimeError("Git repository folder is missing in the ZIP archive.")

        # Create a new repository in the specified directory
        repo = Repo.init(local_repo_path)

        # Add all files from the existing Git repository to the new repository
        for item in os.listdir(git_folder):
            item_path = os.path.join(git_folder, item)
            if os.path.isfile(item_path):
                shutil.copy2(item_path, local_repo_path)

        # Add and commit the changes
        repo.git.add('--all')
        repo.git.commit('-m', 'Initial commit before restoring')

        # Set up the remote
        remote_url = f'https://{token}@github.com/{org_name}/{repo_restored_name}.git'
        origin = repo.create_remote('origin', remote_url)

        # Create and push the 'main' branch to the remote repository
        repo.create_head('main')
        origin.push('main')

        logging.info("Repository restored successfully")

    except GitCommandError as e:
        logging.error(f"Error during repository restoration: {str(e)}")
        logging.error(f"Git command output: {e.stderr}")

    finally:
        logging.info("Removing temporary directory...")
        shutil.rmtree(local_repo_path)

def find_git_folder(repo_path):
    git_folder = os.path.join(repo_path, '.git')
    if os.path.exists(git_folder) and os.path.isdir(git_folder):
        logging.info(f"Git folder found: {git_folder}")
        return git_folder
    else:
      logging.warning("Local repository NOT FOUND!") 
      return None

def create_local_path_from_backup_zip_file(zip_file_path):
    try:
        temp_dir = 'temp_restore'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logging.info(f"Removed existing temporary directory: {temp_dir}")

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        required_files = ['issues.json', 'labels.json', 'repository.json']
        if not all(os.path.exists(os.path.join(temp_dir, file)) for file in required_files):
            raise RuntimeError("Required files are missing in the ZIP archive.")

        return temp_dir

    except FileNotFoundError as e:
        logging.error(f"File not found: {str(e)}")
        raise RuntimeError("Failed to create local path from backup ZIP file.")

    except Exception as e:
        logging.error(f"Error creating local path from backup ZIP file: {str(e)}")
        raise RuntimeError("Failed to create local path from backup ZIP file.")

def find_git_folder(base_path):
    for root, dirs, files in os.walk(base_path):
        if '.git' in dirs:
            return os.path.join(root, '.git')
    return None
        
def restore_labels(repo, labels_data):
    existing_labels = {label.name.lower(): label for label in repo.get_labels()}
    
    for label_info in labels_data:
        label_name = label_info['name'].lower()
        
        if label_name in existing_labels:
            print(f"Label {label_info['name']} already exists, skipping...")
            continue

        try:
            repo.create_label(label_info['name'], label_info['color'])
            print(f"Label {label_info['name']} created successfully.")
        except Exception as e:
            print(f"Error creating label {label_info['name']}: {e}")
            
def restore_issues(repo, issues_data):
    existing_issues = {issue.title.lower(): issue for issue in repo.get_issues()}

    for issue_info in issues_data:
        issue_title = issue_info['title'].lower()

        if issue_title in existing_issues:
            print(f"Issue {issue_info['title']} already exists, skipping...")
            continue

        try:
            repo.create_issue(
                title=issue_info['title'],
                body=issue_info['body'],
                labels=issue_info['labels']
            )
            print(f"Issue {issue_info['title']} created successfully.")
        except Exception as e:
            print(f"Error creating issue {issue_info['title']}: {e}")


def restore_repository(repo, repo_data):
    try:
        repo.edit(
            description=repo_data['description'],
            homepage=repo_data['website']
        )
    except Exception as e:
        print(f"Error updating repository information: {e}")
        
def restore_organization_resources(org_name, access_token, backup_zip_file_path):
    g = Github(access_token)
    org = g.get_organization(org_name)

    try:
        backup_path = create_local_path_from_backup_zip_file(backup_zip_file_path)

        if backup_path:
            try:
                with open(os.path.join(backup_path, "labels.json"), "r") as file:
                    labels_data = json.load(file)

                with open(os.path.join(backup_path, "issues.json"), "r") as file:
                    issues_data = json.load(file)

                with open(os.path.join(backup_path, "repository.json"), "r") as file:
                    repo_data = json.load(file)

                repo_name = repo_data['name']
                current_date = datetime.today().strftime('%Y%m%d')
                #repo_restored_name = f"repo_restored_{current_date}_{repo_name}"
                repo_restored_name = f"{repo_name}"
                org.create_repo(
                        repo_restored_name,
                        allow_rebase_merge=True,
                        auto_init=False,
                        description=repo_data['description'],
                        has_issues=True,
                        has_projects=False,
                        has_wiki=False,
                        private=True,
                    )
                
                repo = org.get_repo(repo_restored_name)
                restore_labels(repo, labels_data)
                restore_issues(repo, issues_data)
                restore_git_repository(repo_restored_name, backup_path, access_token)
                
            finally:
                if os.path.exists(backup_path):
                     logging.info("removing.....")
                   # shutil.rmtree(backup_path)

        else:
            raise RuntimeError("Error creating local path from backup ZIP file.")

    except RuntimeError as e:
        logging.error(str(e))


if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        parser = argparse.ArgumentParser(description='Backup GitHub organization resources.')
        parser.add_argument('-o', '--org_name', type=str, help='GitHub organization name')
        parser.add_argument('-t', '--access_token', type=str, help='backup folder')
        parser.add_argument('-z', '--backup_zip_path', type=str, help='backup zip path')
        args = parser.parse_args()

        org_name = args.org_name or os.environ.get("GITHUB_ORG")
        access_token = args.access_token or os.environ.get("GITHUB_ACCESS_TOKEN")
        backup_zip_path = args.backup_zip_path
        if org_name is None or access_token is None or backup_zip_path is None:
            raise ValueError("Please provide organization name, access token, and the backup.zip path")
        
        restore_organization_resources(org_name, access_token, backup_zip_path)
