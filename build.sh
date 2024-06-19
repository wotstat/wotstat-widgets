#!/bin/bash

d=false

while getopts "v:d" flag
do
    case "${flag}" in
        v) v=${OPTARG};;
        d) d=true;;
    esac
done


rm -rf ./build
mkdir ./build
cp -r ./res ./build

# Set version
configPath="./build/res/scripts/client/gui/mods/wotstat_cef/common/Config.py"
perl -i -pe "s/{{VERSION}}/$v/g" "$configPath"

# Set debug mode
utilsPath="./build/res/scripts/client/gui/mods/wotstat_cef/__init__.py"
if [ "$d" = true ]; then
    echo "Building DEBUG version."
    perl -i -pe "s/'{{DEBUG_MODE}}'/True/g" "$utilsPath"
else
    echo "Building RELEASE version."
    perl -i -pe "s/'{{DEBUG_MODE}}'/False/g" "$utilsPath"
fi

python2 -m compileall ./build

cd ./as3
rm ./bin/*.swf
./build.sh

cd ../

mkdir -p ./build/res/gui/flash
find ./as3/bin -name "*.swf" -exec cp {} ./build/res/gui/flash/ \;

meta=$(<meta.xml)
meta="${meta/\{\{VERSION\}\}/$v}"

cd ./build
echo "$meta" > ./meta.xml

folder="wotstat.cef_$v.wotmod"

rm -rf $folder

zip -dvr -0 -X $folder res -i "*.pyc"
zip -dvr -0 -X $folder res -i "*.swf"
zip -vr -0 -X $folder meta.xml


cp -r ../cefapp res/scripts/client/gui/mods/cefapp
zip -dvr -0 -X $folder res/scripts/client/gui/mods/cefapp

cd ../
cp ./build/$folder $folder
rm -rf ./build
