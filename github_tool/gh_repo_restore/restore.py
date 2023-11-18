import json
import argparse
import os

from github import Github

def restore_labels(repo, labels_data):
    for label_info in labels_data:
        try:
            repo.create_label(label_info['name'], label_info['color'])
        except Exception as e:
            print(f"Error creating label {label_info['name']}: {e}")

def restore_issues(repo, issues_data):
    for issue_info in issues_data:
        try:
            repo.create_issue(
                title=issue_info['title'],
                body=issue_info['body'],
                labels=issue_info['labels']
            )
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

def restore_organization_resources(org_name, access_token, backup_folder):
    g = Github(access_token)
    org = g.get_organization(org_name)

    with open(os.path.join(backup_folder, "labels.json"), "r") as file:
        labels_data = json.load(file)

    with open(os.path.join(backup_folder, "issues.json"), "r") as file:
        issues_data = json.load(file)

    with open(os.path.join(backup_folder, "repository.json"), "r") as file:
        repo_data = json.load(file)

    repo = org.get_repo(repo_data['name'])

    restore_labels(repo, labels_data)
    restore_issues(repo, issues_data)
    restore_repository(repo, repo_data)

if __name__ == "__main__":
        
        parser = argparse.ArgumentParser(description='Backup GitHub organization resources.')
        parser.add_argument('-o', '--org_name', type=str, help='GitHub organization name')
        parser.add_argument('-r', '--access_token', type=str, help='backup folder')
        parser.add_argument('-t', '--backup_folder', type=str, help='backup folder')
        args = parser.parse_args()

        org_name = args.org_name or os.environ.get("GITHUB_ORG")
        access_token = args.access_token or os.environ.get("GITHUB_ACCESS_TOKEN")
        backup_folder = args.backup_folder or os.environ.get("GITHUB_BACKUP_DIR")
    
        restore_organization_resources(org_name, access_token, backup_folder)
