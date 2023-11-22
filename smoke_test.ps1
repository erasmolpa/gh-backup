$orgName = 'erasmolpaorg'
$backupDir = './backups'
$repoNamesRepo = "repo-created-with-terraform"
#$projectID = '3'

$restoreDir = './backups/erasmolpaorg/repo-created-with-terraform_2023-11-22.zip'
python .\github_tool\gh_repo_backup\backup.py -o $orgName -t 'ghp_XXXXX' -d $backupDir -r $repoNamesRepo -rc -pb

#python .\github_tool\gh_project_backup\projects.py -o $orgName -t '${env:GITHUB_ACCESS_TOKEN}' -d $outputDir -p $projectID

python .\github_tool\gh_repo_restore\restore.py -o $orgName -t 'ghp_XXXXX' -d $restoreDir 