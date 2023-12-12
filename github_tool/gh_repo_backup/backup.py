import json
import argparse
import shutil
import time
import zipfile
import os
import datetime
import logging
import gc

from git    import Repo
from git    import GitCommandError
from github import BadCredentialsException 
from github import RateLimitExceededException 
from github import Github 

from azure.storage.blob import ContainerClient

global org_name
global access_token
global output_dir 
global remove_local_repo_dir

global azure_account_name
global azure_account_key
global azure_container_name

  
def github_auth(client_id=None, client_secret=None, access_token=None):
    try:
        if client_id and client_secret:
            g = Github(client_id=client_id, client_secret=client_secret)
        elif access_token:
            g = Github(access_token)
        else:
            raise ValueError("No auth parameters provided.")
        return g

    except BadCredentialsException as e:
        print("Github Invalid Credentials:", e)
    except RateLimitExceededException as e:
        print("Github Rate limit exceeded.", e)
    except Exception as e:
        print("Github Auth issues:", e)

    return None

def create_folder(path):
    os.makedirs(path, exist_ok=True)

def save_data_to_json(data, output_file):
    try:
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error while saving data to JSON: {e}")


def compress_directory(directory):
    
    try:
        current_date = datetime.datetime.now()
        date_str = current_date.strftime('%Y-%m-%d')
        zip_file_name = f'{directory}_{date_str}.zip'
        
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, subdirs, files in os.walk(directory):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, directory)
                    zip_file.write(full_path, relative_path)

        print(f'ZIP file created: {zip_file_name}')
        logging.info(f'ZIP file created: {zip_file_name}')

    except Exception as e:
        error_message = f'Error during compression: {str(e)}'
        print(error_message)
        logging.error(error_message)
        raise
    
def backup_labels(repo, repo_folder):

    try:
        labels = repo.get_labels()
        labels_data = [{"name": label.name, "color": label.color} for label in labels]
        output_file = os.path.join(repo_folder, "labels.json")
        save_data_to_json(labels_data, output_file)
        
    except Exception as e:
        print(f"Error backing up labels for the repository {repo.name}: {e}")
    logging.info("END Backing up repo Labels...")


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

def backup_repository(repo, repo_folder):
    
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
        
        
def clone_repository(repo, repo_backup_folder, token):
    logging.info("Cloning repository...")
    logging.info(f"Parameters: repo_folder={repo_backup_folder}, repo_clone={repo_clone}, repo_name={repo.name}")
    
    now = datetime.datetime.now()
    subfolder_name = f"repo_cloned_{repo.name}_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
    subfolder_path = os.path.join(repo_backup_folder, subfolder_name)
        
    try:
        os.makedirs(subfolder_path, exist_ok=True)
            
        clone_url_with_token = f"https://{token}@github.com/{repo.full_name}.git"
        repo_temp = Repo.clone_from(clone_url_with_token, subfolder_path, no_single_branch=True)
            
        #TODO Should we include and create the Zip at this level ? this could improve in performance the process ?
        #repo_temp.git.archive("--format", "zip", "--output", f"{subfolder_path}.zip", "HEAD")
        logging.info(f"Repository cloned successfully to {subfolder_path}")
            
        if os.listdir(subfolder_path):
            logging.info("Repository folder contains files.")
        else:
            logging.warning("Repository folder is empty.")
                
        gc.collect()
        repo_temp.git.clear_cache()
        return subfolder_path 
            
    except GitCommandError as e:
        logging.error(f"Error during repository cloning: {str(e)}")
        return None 
        
def rmtree(path):
    """Remove the given recursively.

    :note: we use shutil rmtree but adjust its behaviour to see whether files that
        couldn't be deleted are read-only. Windows will not remove them in that case"""

    def onerror(func, path, exc_info):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        try:
            func(path)  # Will scream if still not possible to delete.
        except Exception as ex:
            raise
    return shutil.rmtree(path, False, onerror)


def get_container_client(account_name, account_key, container_name):
    return ContainerClient(account_name, account_key, container_name)

def publish_repositories_backups(container_client, local_directory, container_path=""):
    for root, dirs, files in os.walk(local_directory):
        for file in files:
            if file.endswith(".zip"):
                local_file_path = os.path.join(root, file)
                container_file_path = os.path.join(container_path, file)

                blob_client = container_client.get_blob_client(container_file_path)

                with open(local_file_path, "rb") as data:
                    blob_client.upload_blob(data)

                  
def backup_repository_resources(repo, org_folder, repo_clone, include_labels, include_issues, access_token, publish_backup):
    #TODO Fixme . This should be a env variable instead
    remove_local_repo_dir = False
    repo_backup_folder = os.path.join(org_folder, repo.name)
    create_folder(repo_backup_folder)

    if include_labels:
        backup_labels(repo, repo_backup_folder)
        
    if include_issues:
        backup_issues(repo, repo_backup_folder)
        
    backup_repository(repo, repo_backup_folder)
    
    if repo_clone:
        cloned_folder = clone_repository(repo, repo_backup_folder, access_token )
        compress_directory(repo_backup_folder)
        time.sleep(4)

    if  os.path.exists(cloned_folder) and remove_local_repo_dir:
        try:
            rmtree(cloned_folder)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
               
    if publish_backup: 
       container_client = get_container_client(azure_account_name, azure_account_key, azure_container_name)
       publish_repositories_backups(container_client, repo_backup_folder)

    print("Files uploaded successfully.")

if __name__ == "__main__":   

def backup_organization_resources(org_name, access_token, output_dir, repo_names=None, include_labels=True, include_issues=True, repo_clone=False, publish_backup=False):
    logging.info("INIT  backup_organization_resources Method")
    g = github_auth(access_token=access_token)

    try:
        org = g.get_organization(org_name)
        logging.info("Getting organization details "+ org_name)
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
        logging.info("Getting repositories for the organization " + str(repo_names))
    except Exception as e:
        print(f"Error getting the list of repositories: {e}")
        return

    for repo in repositories:
        if repo_names is None or repo.name in repo_names:
            try:
                backup_repository_resources(repo, org_folder, repo_clone, include_labels, include_issues, access_token, publish_backup)
                org_data["repositories"].append(repo.name)
            except Exception as e:
                print(f"Error backing up the repository {repo.name}: {e}")

    with open(os.path.join(org_folder, "organization.json"), "w") as org_file:
        org_file.write(json.dumps(org_data, indent=4))
        
    logging.info("END backup_organization_resources Method")


if __name__ == "__main__":
    
        ##  TODO Logging based on configuration 
        ##  logging.basicConfig(filename='backup.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        parser = argparse.ArgumentParser(description='Backup GitHub organization resources.')
        
        parser.add_argument('-o', '--org_name', type=str, help='GitHub organization name')
        parser.add_argument('-t', '--access_token', type=str, help='GitHub access token')
        parser.add_argument('-d', '--output_dir', type=str, help='Output directory for backup')
        parser.add_argument('-r', '--repo_names', type=str, nargs='*', help='List of repository names to include in the backup')
        parser.add_argument('-l', '--labels', action='store_true', help='Including labels as part of the backup')
        parser.add_argument('-i', '--issues', action='store_true', help='Including issues as part of the backup')
        parser.add_argument('-rc', '--repo_clone', action='store_true', help='Including whole repo clone as part of the backup')
        parser.add_argument('-pb', '--publish_backup', action='store_true', help='Publish backup as a zip file in remote storage')
        args = parser.parse_args()


        org_name = args.org_name or os.environ.get("GITHUB_ORG")
        access_token = args.access_token or os.environ.get("GITHUB_ACCESS_TOKEN")
        output_dir = args.output_dir or os.environ.get("GITHUB_BACKUP_DIR")
        repo_names = args.repo_names
        repo_clone = args.repo_clone
        include_labels = args.labels
        include_issues = args.issues
        publish_backup = args.publish_backup
        
        if org_name is None or access_token is None or output_dir is None:
            raise ValueError("Please provide organization name, access token, and output directory.")
        
        if publish_backup:
            azure_account_name = os.environ.get("AZURE_ACCOUNT_NAME")
            azure_account_key  = os.environ.get("AZURE_ACCOUNT_KEY")
            azure_container_name = os.environ.get("AZURE_CONTAINER_NAME")
            if azure_account_name is None or azure_account_key is None or azure_container_name is None:
                raise ValueError("Please provide Azure account and container values if you are expecting to publish the backups")
        
        backup_organization_resources(org_name, access_token, output_dir, repo_names, include_labels, include_issues, repo_clone, publish_backup)
