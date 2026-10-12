rm -rf dist/
rm -rf build/
rm -rf __pycache__/

docker build --platform linux/amd64 -t wotstat-cef-builder - < Dockerfile
docker run --rm --platform linux/amd64 -v "$(pwd):/src/" wotstat-cef-builder

cd dist/windows
zip -dvr wotstat.widgets.cef.zip wotstat.widgets.cef/

mv wotstat.widgets.cef.zip ../../
cd ../../

rm -rf dist/
rm -rf build/
rm -rf __pycache__/
find . -type d -name '__pycache__' -exec rm -rf {} +