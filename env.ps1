#pip freeze > requirements.txt
#python -m ensurepip --default-pip
#python -m pip install --upgrade pip
#pip install -r .\requirements.txt


# Establecer variables de entorno
[Environment]::SetEnvironmentVariable("GITHUB_ORG", "erasmolpaorg", [System.EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("GITHUB_USERNAME", "erasmolpa", [System.EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("GITHUB_ACCESS_TOKEN", "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", [System.EnvironmentVariableTarget]::User)

Write-Host "GITHUB_ACCESS_TOKEN:", [Environment]::GetEnvironmentVariable("GITHUB_ACCESS_TOKEN", [System.EnvironmentVariableTarget]::User)
Write-Host "GITHUB_USERNAME:", [Environment]::GetEnvironmentVariable("GITHUB_USERNAME", [System.EnvironmentVariableTarget]::User)

