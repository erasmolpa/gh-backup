$orgName = 'erasmolpaorg'
$outputDir = './'
$repoNamesRepo = "test"
$projectID = '3'

python .\github_tool\gh_repo_backup\backup.py -o $orgName -t '${env:GITHUB_ACCESS_TOKEN}' -d $outputDir -r $repoNamesRepo

python .\github_tool\gh_project_backup\projects.py -o $orgName -t '${env:GITHUB_ACCESS_TOKEN}' -d $outputDir -p $projectID

