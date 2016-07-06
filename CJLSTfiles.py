import re
import subprocess

folders = {}

def exists(maindir, foldername):
    global folders
    if maindir not in folders:
        folders[maindir] = xrdls(maindir)
    return foldername in folders[maindir]


def xrdls(maindir):
    print maindir
    assert maindir.split("//")[0] == "root:" and len(maindir.split("//")) == 3
    connect = maindir.split("//")[1]
    cd = "/" + maindir.split("//")[2]
    command = """
                 echo '
                   connect {}
                   cd {}
                   ls
                 ' | xrd
              """.format(connect, cd)
    lsoutput = subprocess.check_output(command, shell=True)
    result = []
    for line in lsoutput.split("\n"):
        if 'dr-x' in line:
            result.append(line.split("/")[-1])
    return result

def listfolders(maindir, match):
    if maindir not in folders:
        folders[maindir] = xrdls(maindir)
    return [folder for folder in folders[maindir] if re.match(match, folder)]

if __name__ == "__main__":
    print listfolders("root://lxcms03//data3/Higgs/160624", "WplusH[0-9]*")
    print listfolders("root://lxcms03//data3/Higgs/160225", "WplusH[0-9]*")
