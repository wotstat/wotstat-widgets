#!/bin/bash

debug=False

as3Only=False
serverOnly=False
pythonOnly=False

while getopts "v:aspd" flag
do
  case "${flag}" in
    v) v=${OPTARG};;
    d) debug=True;;
    a) as3Only=True;;
    s) serverOnly=True;;
    p) pythonOnly=True;;
  esac
done



echo "______PLAN:______"
echo "Version: $v"
echo "Debug: $debug"
echo "_________________"
echo ""

cef_shasum=$(find ./cef-server/src/ -type f -exec cat {} + | shasum -a 256 | awk '{print $1}')
echo "CEF shasum: $cef_shasum"
folder="wotstat.widgets_$v.wotmod"
rm -rf $folder


rm -rf ./build
mkdir ./build


build_as3() {
  cd ./mod/as3
  rm ./bin/*.swf
  ./build.sh
  cd ../../
}

build_python() {
  cp -r ./mod/res ./build

  # Set version and debug mode
  configPath="./build/res/scripts/client/gui/mods/wotstat_widgets/common/Config.py"
  mainPath="./build/res/scripts/client/gui/mods/wotstat_widgets/WotstatWidget.py"
  perl -i -pe "s/{{VERSION}}/$v/g" "$configPath"
  perl -i -pe "s/'{{DEBUG_MODE}}'/$debug/g" "$mainPath"
  perl -i -pe "s/{{CEF_SERVER_CHECKSUM}}/$cef_shasum/g" "$mainPath"

  python2 -m compileall ./build
  find ./build -name "*.py" -type f -exec rm {} \;
}

build_server() {
  cd ./cef-server
  ./build.sh
  cd ../
}

full_build() {
  build_server
  build_python
  build_as3
}

if [ "$as3Only" = True ] || [ "$serverOnly" = True ] || [ "$pythonOnly" = True ]; then

    if [ "$serverOnly" = True ] || [ ! -f ./cef-server/wotstat.widgets.cef.zip ]; then
        build_server
    fi

    build_python

    if [ "$as3Only" = True ]; then
        build_as3
    fi
else
    full_build
fi


mkdir -p ./build/res/gui/flash
find ./mod/as3/bin -name "*.swf" -exec cp {} ./build/res/gui/flash/ \;
cp -r ./mod/as3/assets ./build/res/gui/flash/wotstatCefAssets

meta=$(<meta.xml)
meta="${meta/\{\{VERSION\}\}/$v}"
echo "$meta" > ./build/meta.xml
cd ./build

zip -dvr -0 -X $folder res -i "*.pyc"
zip -dvr -0 -X $folder res -i "*.swf"
zip -dvr -0 -X $folder res -i "*.png"
zip -vr -0 -X $folder meta.xml


echo "CEF shasum: $cef_shasum"
cp ../cef-server/wotstat.widgets.cef.zip wotstat.widgets.cef.$cef_shasum.zip
mkdir -p wotstat.widgets.cef
echo "$cef_shasum" > wotstat.widgets.cef/checksum
zip -dvr -0 -X wotstat.widgets.cef.$cef_shasum.zip wotstat.widgets.cef/checksum
rm -rf wotstat.widgets.cef

cp wotstat.widgets.cef.$cef_shasum.zip ../wotstat.widgets.cef.$cef_shasum.zip

cd ../
cp ./build/$folder $folder
rm -rf ./build