FROM cdrx/pyinstaller-windows AS python
FROM ubuntu:24.04
ENV WINEARCH=win64 WINEPREFIX=/wine WINEDEBUG=-all WINEDLLOVERRIDES="winemenubuilder.exe=d;mscoree=d;mshtml=d"
RUN apt-get update && apt-get install -y --no-install-recommends wine64 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=python /wine /wine
WORKDIR /src
ENTRYPOINT ["/usr/lib/wine/wine64", "/wine/drive_c/Python37/python.exe", "-m", "PyInstaller", "--clean", "-y", "--distpath", "dist/windows", "--workpath", "/tmp/pyinstaller", "main.spec"]
