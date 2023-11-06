Example of running the python code :

````
python gh_backup.py --org_name 'erasmolpaorg' --access_token 'ghp_XEc92aKqvJZA6kCRSXXXXXXXXXX' --output_dir './'

``

`` name: Backup Using Github-backup CLI library

on:
  push:
    branches: '*'

jobs:
  backup:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout del código fuente
      uses: actions/checkout@v2

    - name: Configurar Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11

    - name: install github-backup
      run: pip install github-backup==0.43.1

    - name: execute github-backup
      env:
        ORGANIZATION: erasmolpaorg
      run: github-backup $ORGANIZATION --private --incremental --token ${{ secrets.ADMIN_TOKEN }} -o . --all
   
    - name: Commit and Push
      env:
        GIT_USERNAME: ${{ secrets.ADMIN_USER_NAME }}
        GIT_USER_EMAIL: ${{ secrets.ADMIN_USER_EMAIL }}
        GIT_TOKEN: ${{ secrets.ADMIN_TOKEN }}
      run: |
        git config user.name "erasmolpa"
        git config user.email "erasmolpa@gmail.com"
        git add *
        git commit -m "Auto commit from GitHub Action"
        git push
``