import os
import json
from github import Github

def create_folder(path):
    os.makedirs(path, exist_ok=True)

def backup_labels(repo, repo_folder):
    try:
        labels = repo.get_labels()
        labels_data = [{"name": label.name, "color": label.color} for label in labels]
        with open(os.path.join(repo_folder, "labels.json"), "w") as labels_file:
            labels_file.write(json.dumps(labels_data, indent=4))
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

        with open(os.path.join(repo_folder, "issues.json"), "w") as issues_file:
            issues_file.write(json.dumps(issues_data, indent=4))
    except Exception as e:
        print(f"Error backing up issues for the repository {repo.name}: {e}")

def backup_repository(repo, org_folder):
    repo_folder = os.path.join(org_folder, repo.name)
    create_folder(repo_folder)

    backup_labels(repo, repo_folder)
    backup_issues(repo, repo_folder)

    repo_data = {
        "name": repo.name,
        "description": repo.description,
        "website": repo.homepage,
        "language": repo.language,
        "created_at": repo.created_at.isoformat(),
        "updated_at": repo.updated_at.isoformat()
    }
    with open(os.path.join(repo_folder, "repository.json"), "w") as repo_file:
        repo_file.write(json.dumps(repo_data, indent=4))

def backup_organization_resources(org_name, access_token, output_dir):
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
        try:
            backup_repository(repo, org_folder)
            org_data["repositories"].append(repo.name)
        except Exception as e:
            print(f"Error backing up the repository {repo.name}: {e}")

    with open(os.path.join(org_folder, "organization.json"), "w") as org_file:
        org_file.write(json.dumps(org_data, indent=4))

if __name__ == "__main__":
    
    org_name = os.environ.get("GITHUB_ORG")
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
    output_dir = os.environ.get("GITHUB_BACKUP_DIR")

    backup_organization_resources(org_name, access_token, output_dir)
