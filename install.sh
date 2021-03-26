# #!/bin/bash
# set -ex
# cd "$(dirname "$0")"
# if [ -z "$1" ]
#   then
#     echo 'No module specified'
#     exit 1
# fi
# project=$1
# installation_dir=/usr/local/bin/atlcli/${project}
# if [ ! -d $installation_dir ]; then
# 	sudo mkdir -p $installation_dir
# 	sudo unzip ${project}/build/${project}.zip -d /usr/local/bin/atlcli/jira
# else
# 	echo 'Already installed at $installation_dir'
# fi
# export PATH=/usr/local/bin/atlcli/jira:$PATH
# echo 'export PATH=/usr/local/bin/atlcli/jira:$PATH' >> ~/.bash_profile
