# GitHub Backup Script

This script is designed to backup GitHub organization resources, including repositories, issues, labels, and more.

## Features

- Backup organization details, repositories, labels, and issues.
- Optionally clone repositories for a full backup.
- Option to publish the backup as a zip file in remote storage.

## Prerequisites

- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`)

## Usage

```bash
python backup.py -o <organization_name> -t <access_token> -d <output_directory> -r <repo_names> -rc -pb
```
## Parameters

| Option                | Description                                     | Required | Default |
|-----------------------|-------------------------------------------------|----------|----------|
| -o or --org_name      | GitHub organization name.                       | Yes      | ""|
| -t or --access_token  | GitHub access token.                            | Yes      |""|
| -d or --output_dir    | Output directory for the backup.                | Yes      |""|
| -r or --repo_names    | List of repository names to include in the backup. | No    |""|
| -rc or --repo_clone   | Include whole repository clone as part of the backup. | No       |False|
| -pb or --publish_backup| Publish backup as a zip file in remote storage. | No       |False|
| -l or --labels         | include labels as part of the backup | No       |True       |
| -i or --issues         | include issues as part of the backup | No       |True       |
## Examples 

# Basic backup without repository cloning
python backup.py -o my_organization -t my_access_token -d /path/to/backup

# Backup specific repositories and clone them
python backup.py -o my_organization -t my_access_token -d /path/to/backup -r repo1 repo2 -rc

# Publish backup as a zip file
python backup.py -o my_organization -t my_access_token -d /path/to/backup -pb

