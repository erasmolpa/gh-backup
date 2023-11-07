import os
from github import Github
import json

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

def backup_github_project(username, project_id, access_token, output_dir):
    try:
        g = Github(access_token)
        project = g.get_project(int(project_id))
        get_project_data(project, output_dir)
    except Exception as e:
        print(f"Error while backing up GitHub project: {e}")

if __name__ == "__main":
    
    username = os.environ.get("GITHUB_USERNAME")
    project_id = os.environ.get("GITHUB_PROJECT_ID")
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
    output_dir = os.environ.get("GITHUB_BACKUP_DIR")
 
    backup_github_project(username, project_id, access_token, output_dir)
