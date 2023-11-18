#### Enable workflow permissions 
In the repository setting, modify the actions settings, Workflow permissions for enabling read-write 

https://github.com/erasmolpa/gh-backup/settings/actions

#### Example of running the python code :

backup all repos in the organization 

````
python gh_backup.py --org_name 'erasmolpaorg' --access_token 'ghp_XXXX' --output_dir './'

```

backup only specific repos 

````
python gh_backup.py --org_name 'erasmolpaorg' --access_token 'XXXXXXXXXXXXX' --output_dir './' --repo_names 'test' 'repo2'

``

including the whole repo as part of the backup
````
python gh_backup.py --org_name 'erasmolpaorg' --access_token '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' --output_dir './' --repo_names 'test' --repo_clone

``

including the whole repo as part of the backup
````
python gh_backup_project.py --org_name 'erasmolpaorg' --access_token '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' --output_dir './' --project_ids '1'


Restoring repo 

````
python gh_restore.py  --org_name 'erasmolpaorg' --access_token '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' --backup_folder './erasmolpaorg/test'


