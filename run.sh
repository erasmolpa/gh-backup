export ACCESS_TOKEN=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
ORGANIZATION=erasmolpaorg
REPO=kubernetes
# e.g. git@github.com:docker/cli.git
github-backup $ORGANIZATION -t $ACCESS_TOKEN -o . -i -l DEBUG --all