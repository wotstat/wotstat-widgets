rm -rf dist/
rm -rf build/
rm -rf __pycache__/

docker run --rm -v "$(pwd):/src/" cdrx/pyinstaller-windows

cd dist/windows
zip -dvr wotstat.widget.cef.zip wotstat.widget.cef/

mv wotstat.widget.cef.zip ../../
cd ../../

rm -rf dist/
rm -rf build/
rm -rf __pycache__/
