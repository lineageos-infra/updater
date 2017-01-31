export FLASK_APP=app.py

DEVICES=(bacon flo deb i9300 i9305 d2att d2vzw d2spr d2tmo jflte jfltespr jfltetmo jflteatt jfltevzw klte klteusc klteatt kltevzw kltespr kltetmo tenderloin n5100 n5110 n5120 evita mako hammerhead angler bullhead marlin sailfish cancro)

for i in {0..99}; do

rand=$[$RANDOM % 32]
DEVICE=${DEVICES[$rand]}
FILENAME=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
VERSION=14.1
DATETIME="2017-07-07"
ROMTYPE="nightly"
MD5SUM=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
URL=https://mirrobits.lineageos.org/full/${DEVICE}/${DATETIME}/${FILENAME}


flask addrom --filename $FILENAME --device $DEVICE --version $VERSION --datetime $DATETIME --romtype $ROMTYPE --md5sum $MD5SUM --url $URL

done
