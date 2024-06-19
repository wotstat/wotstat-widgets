import ResMgr
import os

def copyFile(source, target):
  targetDir = os.path.dirname(target)
  if not os.path.exists(targetDir):
    os.makedirs(targetDir)
  data = ResMgr.openSection(source).asBinary
  if data:
    with open(target, "wb") as targetFile:
      targetFile.write(data)

def copyDir(source, target):
  for file in ResMgr.readDirectory(source):
    sourcePath = os.path.join(source, file)
    targetPath = os.path.join(target, file)
    if ResMgr.isDir(file):
      copyDir(sourcePath, targetPath)
    else:
      copyFile(sourcePath, targetPath)
