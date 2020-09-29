import pexpect
import sys
import time
import os
import re
import multiprocessing
import subprocess
import glob

# 解析
## ====================
import json
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper
## ====================

subprocess.run("pwd")
user = sys.argv[1]
branch = sys.argv[2]

TIMEOUT = 10

BASE = "/home/own/MengXia"

OUTPUT_FILE = BASE + "/warehouse/" + "zCore" + "_realm/" + user + "/logfile/" + branch + "/linux" + "/libc_output.txt"

os.chdir(BASE + "/warehouse/" + "zCore" + "_realm/" + user + "/" + "zCore")
subprocess.run("git checkout " + branch, shell=True)
subprocess.run("make rootfs && make libc-test", shell=True)
subprocess.run("cargo build --release -p linux-loader", shell=True)
start = time.time()
print("开始计时")

with open(OUTPUT_FILE, "w") as output:
    index = 1
    for path in glob.glob("rootfs/libc-test/src/*/*.exe"):
        path = path[len('rootfs'):]
        try:
            print(str(index) + "  running : ", path)

            p = subprocess.run("cargo run --release -p linux-loader " + path,
                               shell=True,
                               stdout=output,
                               stderr=output,
                               timeout=TIMEOUT,
                               check=True,
                               encoding="utf-8")

            print()

            output.write(
                str(index) + "  :  " +
                "============================ PASSED ============================\n"
            )
            output.write(path + "\n")
            output.write(
                "============================ PASSED ============================"
            )
            output.write("\n\n\n\n")
            output.flush()

        except subprocess.CalledProcessError:
            print()

            output.write(
                str(index) + "  :  " +
                "============================ ERROR ============================\n"
            )
            output.write(path + "\n")
            output.write(
                "============================ ERROR ============================"
            )
            output.write("\n\n\n\n")
            output.flush()

        except subprocess.TimeoutExpired:
            print()
            output.write(
                str(index) + "  :  " +
                "============================ TIMEOUT ============================\n"
            )
            output.write(path + "\n")
            output.write(
                "============================ TIMEOUT ============================"
            )
            output.write("\n\n\n\n")
            output.flush()
        index += 1

os.system('killall linux-loader')

end = time.time()
os.chdir(BASE)
print('用时--times{:.3f}'.format(end - start))
