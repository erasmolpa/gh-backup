$orgName = 'erasmolpaorg'
$accessTokenRepo = $env:GITHUB_ACCESS_TOKEN
$outputDir = './'
$repoNamesRepo = "test"
$accessTokenProject = $env:GITHUB_ACCESS_TOKEN
$projectID = '3'

$backupScriptRepo = ".\github_tool\gh_repo_backup\backup.py"

$repoBackupCommand = "python $backupScriptRepo -o '$orgName' -t $accessTokenRepo -d '$outputDir' -r '$repoNamesRepo'"

Invoke-Expression -Command $repoBackupCommand


$backupScriptProject = ".\github_tool\gh_project_backup\projects.py"

$projectBackupCommand = "python $backupScriptProject -o '$orgName' -t $accessTokenProject -d '$outputDir' -p '$projectID'"


Invoke-Expression -Command $projectBackupCommand
