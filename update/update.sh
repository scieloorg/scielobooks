#!/bin/bash
#
# Script to update SciELO Book Enviroment
#
#
. update_config.sh

DAY=`/bin/date +%Y%m%d`

echo "[INITIALIZING $name_app UPDATE]"

echo "[----+GENERATING BACKUP FILE AND COPY TO: $path_target]"

tar -c -f $path_target/$name_app$DAY-BKP.tar --totals $path_app

echo "BACKUP FILE: $path_target/$name_app$DAY-BKP.tar"

echo "[----+GET UPDATE FROM $git_url]"
 
git pull $git_url

echo "[-----+TOUCH ON FILE: $path_config_file]"

touch $path_config_file

echo "[-----+RESTARTING APACHE]"

$path_server

echo "[FINISH THE UPDATE OF $name_app]"
