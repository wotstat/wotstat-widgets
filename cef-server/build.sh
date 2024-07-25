rm -rf dist/
rm -rf build/
rm -rf __pycache__/

docker run --rm -v "$(pwd):/src/" cdrx/pyinstaller-windows

cd dist/windows
zip -dvr wotstat.widgets.cef.zip wotstat.widgets.cef/

mv wotstat.widgets.cef.zip ../../
cd ../../

rm -rf dist/
rm -rf build/
rm -rf __pycache__/
