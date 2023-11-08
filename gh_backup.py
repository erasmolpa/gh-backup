import os
import json
import argparse

import datetime
from git import Repo
from git import GitCommandError
from github import Github 

global org_name
global access_token
global output_dir 

def create_folder(path):
    os.makedirs(path, exist_ok=True)

def save_data_to_json(data, output_file):
    try:
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error while saving data to JSON: {e}")
        
def backup_labels(repo, repo_folder):
    try:
        labels = repo.get_labels()
        labels_data = [{"name": label.name, "color": label.color} for label in labels]
        output_file = os.path.join(repo_folder, "labels.json")
        save_data_to_json(labels_data, output_file)
        
    except Exception as e:
        print(f"Error backing up labels for the repository {repo.name}: {e}")


def backup_issues(repo, repo_folder):
    try:
        issues = repo.get_issues(state="all")
        issues_data = []
        for issue in issues:
            issue_info = {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                "user": issue.user.login,
                "labels": [label.name for label in issue.get_labels()]
            }
            issues_data.append(issue_info)
            
        output_file = os.path.join(repo_folder, "issues.json")
        save_data_to_json(issues_data, output_file)
        
    except Exception as e:
        print(f"Error backing up issues for the repository {repo.name}: {e}")

def backup_repository(repo, repo_folder, repo_clone):
    
    repo_data = {
        "name": repo.name,
        "description": repo.description,
        "website": repo.homepage,
        "language": repo.language,
        "created_at": repo.created_at.isoformat(),
        "updated_at": repo.updated_at.isoformat()
    }
    
    output_file = os.path.join(repo_folder, "repository.json")
    save_data_to_json(repo_data, output_file)
            
    clone_repository(repo, repo_folder, repo_clone)

    #if create_zip:
    #    print("TODO. Not implemented yet")  
        
        
def clone_repository(repo, repo_folder, repo_clone):
    if repo_clone:
        now = datetime.datetime.now()
        subfolder_name = f"{repo.name}_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
        subfolder_path = os.path.join(repo_folder, subfolder_name)
        try:
            Repo.clone_from(repo.clone_url, subfolder_path,  no_single_branch=True)
        except GitCommandError as e:
            print(f"Error getting the list of repositories: {e}")
        return
        
        
def backup_repository_resources(repo, org_folder, repo_clone):
    repo_folder = os.path.join(org_folder, repo.name)
    create_folder(repo_folder)

    backup_labels(repo, repo_folder)
    backup_issues(repo, repo_folder)
    backup_repository(repo, repo_folder, repo_clone)


def backup_organization_resources(org_name, access_token, output_dir, repo_names=None, repo_clone=False):
    g = Github(access_token)

    try:
        org = g.get_organization(org_name)
    except Exception as e:
        print(f"Error getting the organization: {e}")
        return

    org_folder = os.path.join(output_dir, org_name)
    create_folder(org_folder)

    org_data = {
        "name": org_name,
        "description": org.description,
        "website": org.blog,
        "location": org.location,
        "repositories": []
    }

    try:
        repositories = org.get_repos()
    except Exception as e:
        print(f"Error getting the list of repositories: {e}")
        return

    for repo in repositories:
        if repo_names is None or repo.name in repo_names:
            try:
                backup_repository_resources(repo, org_folder, repo_clone)
                #backup_repository_resources(repo, org_folder, repo_clone, create_zip)
                org_data["repositories"].append(repo.name)
            except Exception as e:
                print(f"Error backing up the repository {repo.name}: {e}")


    with open(os.path.join(org_folder, "organization.json"), "w") as org_file:
        org_file.write(json.dumps(org_data, indent=4))

if __name__ == "__main__":
  
        parser = argparse.ArgumentParser(description='Backup GitHub organization resources.')
        parser.add_argument('-o', '--org_name', type=str, help='GitHub organization name')
        parser.add_argument('-t', '--access_token', type=str, help='GitHub access token')
        parser.add_argument('-d', '--output_dir', type=str, help='Output directory for backup')
        parser.add_argument('-r', '--repo_names', type=str, nargs='*', help='List of repository names to include in the backup')
        parser.add_argument('-rc', '--repo_clone', action='store_true', help='Including whole repo clone as part of the backup')
        #parser.add_argument('-cz','--create_zip', action='store_true', help='create a zip file ')
        args = parser.parse_args()


        org_name = args.org_name or os.environ.get("GITHUB_ORG")
        access_token = args.access_token or os.environ.get("GITHUB_ACCESS_TOKEN")
        output_dir = args.output_dir or os.environ.get("GITHUB_BACKUP_DIR")
        repo_names = args.repo_names
        repo_clone = args.repo_clone
        #create_zip = args.create_zip
        if org_name is None or access_token is None or output_dir is None:
            raise ValueError("Please provide organization name, access token, and output directory.")
        
        backup_organization_resources(org_name, access_token, output_dir, repo_names, repo_clone)
        #backup_organization_resources(org_name, access_token, output_dir, repo_names, repo_clone, create_zip)
