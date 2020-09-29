import pexpect
import os
import sys
import subprocess
import time

subprocess.run("pwd")
user = sys.argv[1]
branch = sys.argv[2]

#===============File Config========================

BASE = "/home/own/MengXia"

LOGFILE = BASE + "/warehouse" + "/rCore-Tutorial" + "_realm/" + user + "/logfile/" + branch + "/qemu" + "/logfile.txt"
RESULT = BASE + "/warehouse" + "/rCore-Tutorial" + "_realm/" + user + "/result/" + branch + "/qemu" + "/result.txt"
CONFIG = BASE + "/warehouse" + "/rCore-Tutorial" + "_realm/" + "config" + "/libc_test.txt"

#==============================================


class Tee:
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()


def main():

    with open(RESULT, "w", encoding='utf-8', errors='ignore'):
        pass

    child = pexpect.spawn("make run", timeout=30, encoding='utf-8')

    child.logfile = Tee(LOGFILE, "w")

    child.expect(">>")
    child.sendline("hello_world")

    child.expect(">>")

    child.sendline("fantastic_text")

    index = child.expect([">>", pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        with open(RESULT, "a", encoding='utf-8', errors='ignore') as f:
            f.writelines("finished\n")
    elif index == 1:
        with open(RESULT, "a", encoding='utf-8', errors='ignore') as f:
            f.writelines("EOF\n")
    elif index == 1:
        with open(RESULT, "a", encoding='utf-8', errors='ignore') as f:
            f.writelines("TIMEOUT\n")


os.chdir(BASE + "/warehouse/" + "rCore-Tutorial" + "_realm/" + user + "/" +
         "rCore-Tutorial")
subprocess.run("git checkout " + branch, shell=True)
main()
os.chdir(BASE)
