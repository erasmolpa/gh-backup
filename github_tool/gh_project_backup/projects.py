import json
import argparse

from github import Github 

import os
import logging

from github import BadCredentialsException 
from github import RateLimitExceededException 
from github import Github 

global org_name
global access_token
global output_dir 

def get_project_data(project, output_dir):
    try:
        project_data = {
            "name": project.name,
            "columns": []
        }

        columns = project.get_columns()
        for column in columns:
            column_data = get_column_data(column)
            project_data["columns"].append(column_data)

        output_file = os.path.join(output_dir, "github_project_backup.json")
        save_data_to_json(project_data, output_file)
        print(f"GitHub project backup saved to '{output_dir}/github_project_backup.json'")
    except Exception as e:
        print(f"Error while getting project data: {e}")

def get_column_data(column):
    try:
        column_data = {
            "name": column.name,
            "cards": []
        }

        cards = column.get_cards()
        for card in cards:
            card_data = get_card_data(card)
            column_data["cards"].append(card_data)

        return column_data
    except Exception as e:
        print(f"Error while getting column data: {e}")
        return {"name": column.name, "cards": []}

def get_card_data(card):
    try:
        card_data = {
            "note": card.note
        }

        if card.content:
            card_data["content_url"] = card.content.html_url

        return card_data
    except Exception as e:
        print(f"Error while getting card data: {e}")
        return {"note": card.note}

def save_data_to_json(data, output_file):
    try:
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error while saving data to JSON: {e}")

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
        
def backup_github_project(organization_name, project_ids, access_token, output_dir):
    logging.info("INIT backup_organization_resources Method")
    g = github_auth(access_token=access_token)

    project_details_list = []

    try:
        org = g.get_organization(organization_name)
        logging.info("Getting organization details " + organization_name)
    except Exception as e:
        print(f"Error getting the organization: {e}")
        return
    
    org_projects = org.get_projects()
    
    for project_id in project_ids:
        # Find the project with the specified ID
        project = None
        for org_project in org_projects:
            if org_project.id == int(project_id):
                project = org_project
                break

        # Print some debug information
        print(f"Searching for project with ID {project_id}")
        print("Organization projects:")
        for org_project in org_projects:
            print(f" - {org_project.id}: {org_project.name}")

        # Check if the project is found
        if project:
            project_details = {
                "Project ID": project.id,
                "Project Name": project.name,
                "Project State": project.state,
                "Created At": str(project.created_at),
                # Add more details as needed
            }

            # Get the columns of the project
            columns = project.get_columns()

            # Add column details to the dictionary
            project_details["Columns"] = []

            for column in columns:
                column_details = {
                    "Column Name": column.name,
                    "Cards": [card.get_content().title for card in column.get_cards()]
                }
                project_details["Columns"].append(column_details)

            project_details_list.append(project_details)
            get_project_data(project, output_dir)
        else:
            print(f"Project with ID {project_id} not found.")

      
if __name__ == "__main__":
    
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        parser = argparse.ArgumentParser(description='Backup GitHub organization resources.')
        parser.add_argument('-o', '--org_name', type=str, help='GitHub organization name')
        parser.add_argument('-p', '--project_ids', type=str, nargs='*', help='List of Github Project IDs names to include in the backup')
        parser.add_argument('-t', '--access_token', type=str, help='GitHub access token')
        parser.add_argument('-d', '--output_dir', type=str, help='Output directory for backup')
        args = parser.parse_args()

        org_name = args.org_name or os.environ.get("GITHUB_ORG")
        project_ids = args.project_ids or os.environ.get("GITHUB_PROJECT_ID")
        access_token = args.access_token or os.environ.get("GITHUB_ACCESS_TOKEN")
        output_dir = args.output_dir or os.environ.get("GITHUB_BACKUP_DIR")
    
        
        if project_ids is None or access_token is None or output_dir is None:
            raise ValueError("Please provide project_id, access token, and output directory.")
        
        backup_github_project(org_name,project_ids, access_token, output_dir)
 
    