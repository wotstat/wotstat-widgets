#!/bin/bash

debug=False
modOnly=False
pythonOnly=False

while getopts "v:dmp" flag
do
  case "${flag}" in
    v) v=${OPTARG};;
    d) debug=True;;
    m) modOnly=True;;
    p) pythonOnly=True;;
  esac
done



echo "______PLAN:______"
echo "Version: $v"
echo "Debug: $debug"

if [ "$pythonOnly" = true ]; then
  echo "Python Only (without cef-server and as3)"
elif [ "$modOnly" = true ]; then
  echo "Mod Only (python + as3)"
else
  echo "Full Build"
fi

echo "_________________"
echo ""


folder="wotstat.cef_$v.wotmod"
rm -rf $folder


rm -rf ./build
mkdir ./build


# BUILD PYTHON
echo "Build Python"
cp -r ./mod/res ./build

# Set version and debug mode
configPath="./build/res/scripts/client/gui/mods/wotstat_cef/common/Config.py"
mainPath="./build/res/scripts/client/gui/mods/wotstat_cef/WotstatWidget.py"
perl -i -pe "s/{{VERSION}}/$v/g" "$configPath"
perl -i -pe "s/'{{DEBUG_MODE}}'/$debug/g" "$mainPath"

python2 -m compileall ./build
find ./build -name "*.py" -type f -exec rm {} \;



# BUILD AS3
if [ "$pythonOnly" = False ]; then
  cd ./mod/as3
  rm ./bin/*.swf
  ./build.sh
  cd ../../
fi  

mkdir -p ./build/res/gui/flash
find ./mod/as3/bin -name "*.swf" -exec cp {} ./build/res/gui/flash/ \;



# BUILD SERVER
if [ "$modOnly" = False ] && [ "$pythonOnly" = False ] || [ ! -f ./cef-server/wotstat.widget.cef.zip ]; then
  cd ./cef-server
  ./build.sh
  cd ../
fi



meta=$(<meta.xml)
meta="${meta/\{\{VERSION\}\}/$v}"
echo "$meta" > ./build/meta.xml
cd ./build


zip -dvr -0 -X $folder res -i "*.pyc"
zip -dvr -0 -X $folder res -i "*.swf"
zip -vr -0 -X $folder meta.xml

cp ../cef-server/wotstat.widget.cef.zip res/wotstat.widget.cef.zip
zip -dvr -0 -X $folder res/wotstat.widget.cef.zip

cd ../
cp ./build/$folder $folder
rm -rf ./build