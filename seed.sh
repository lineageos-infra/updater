export FLASK_APP=app.py

DEVICES=(mako bullhead angler shamu whale potato orange cabbage cat dog pillow orangutang i9300 glass phone pen wheatthins thingy mangos DONGS stool cabinent desk table counter fridge copper iron silver lego eggo waffle)

for i in {0..99}; do

rand=$[$RANDOM % 32]
DEVICE=${DEVICES[$rand]}
FILENAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
VERSION=14.1
DATETIME="2012-07-07"
ROMTYPE="nightly"
MD5SUM=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
URL=https://mirrobits.lineageos.org/full/${DEVICE}/${DATETIME}/${FILENAME}


flask addrom --filename $FILENAME --device $DEVICE --version $VERSION --datetime $DATETIME --romtype $ROMTYPE --md5sum $MD5SUM --url $URL --available true

done
