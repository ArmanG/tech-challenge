 #!/bin/bash
 
 repository="https://github.com/cryoem-uoft/structura-techchallenge-assets.git"
 
 mongod="/usr/local/mongodb/bin/mongod"
 mongod_data="/Users/armanghassemi/techChallenge/mongodb_data"
 mongod_log="/Users/armanghassemi/techChallenge/mongodb_log/mongodb.log"
 prog="mongod.sh"
 RETVAL=0

 git clone "$repository"

grep_mongo=`ps aux | grep -v grep | grep "${mongod}"`

if [ -n "${grep_mongo}" ]
then
echo "MongoDB is already running."
else
echo "Start MongoDB."
`${mongod} --dbpath ${mongod_data} --logpath ${mongod_log} --fork --logappend`
RETVAL=$?
fi

chmod 755 mongoSetup.py
python mongoSetup.py

exit $RETVAL
