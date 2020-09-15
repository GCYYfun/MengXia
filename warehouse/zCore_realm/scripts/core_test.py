import pexpect
import sys
import time
import os
import re
import multiprocessing
import subprocess

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

OUTPUT_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/logfile/" + branch + "/output.txt"
RESULT_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/result/" + branch +  "/test-result.txt"
TEST_CASES_FILE  = BASE + "/warehouse/" + "zCore" + "_realm/" + "config/" + "test_case.yaml"
ALL_CASES  = BASE + "/warehouse/" + "zCore" + "_realm/" + "config/" + "all-test-cases.txt"
STATISTIC_BAD_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/help_info/" + branch + "/test-statistic-bad.txt"
STATISTIC_GOOD_FILE = BASE + "/warehouse/" + "zCore" + "_realm/" + user + "/help_info/" + branch + "/test-statistic-good.txt"

PROCESSES = 1
PREBATCH = 1

IMG = "zCore/target/x86_64/release/disk.qcow2"
ESP = "zCore/target/x86_64/release/esp"
OVMF = "rboot/OVMF.fd"


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

def running(index_num,line,fd):

    print('[running]    '+str(index_num)+'    '+line)
    write_arg(line)

    child = pexpect.spawn("qemu-system-x86_64 \
                                -smp 1 -machine q35 \
                                -cpu Haswell,+smap,-check,-fsgsbase \
                                -drive if=pflash,format=raw,readonly,file="+OVMF+" \
                                -drive format=raw,file=fat:rw:"+ ESP +" \
                                -drive format=qcow2,file="+IMG+",id=disk,if=none \
                                -device ich9-ahci,id=ahci \
                                -device ide-drive,drive=disk,bus=ahci.0 \
                                -serial mon:stdio -m 4G -nic none \
                                -device isa-debug-exit,iobase=0xf4,iosize=0x04 \
                                -accel kvm -cpu host,migratable=no,+invtsc  \
                                -display none -nographic",
                                timeout=TIMEOUT, encoding='utf-8')

    # with open(OUTPUT_FILE, "a") as f:
    child.logfile = fd
    
    index = child.expect(['PASSED','FAILED','panicked', pexpect.EOF, pexpect.TIMEOUT,'Running 0 test from 0 test case'])
    result = ['PASSED','FAILED','PANICKED', 'EOF', 'TIMEOUT','UNKNOWN'][index]
    print('[result]    '+str(index_num)+'    '+line+'    '+result)
    with open(RESULT_FILE, "a") as f:
        f.write('[result]    '+str(index_num)+'    '+line+'    '+result+'\n')

def write_arg(line):
    content=[]
    with open(ESP + "/EFI/Boot/rboot.conf","r") as f:
        content = f.readlines()
    i=0
    while i < len(content):
        if content[i].startswith("cmdline"):
            content[i] = "cmdline=LOG=warn:userboot=test/core-standalone-test:userboot.shutdown:core-tests="+line
        i = i + 1
    with open(ESP + "/EFI/Boot/rboot.conf","w") as f:
        f.writelines(content)

def perpare_data(name):
    with open(ALL_CASES, "r") as f:
        lines = f.readlines()
    return lines
    # with open(TEST_CASES_FILE, "r") as f:
    #     d = f.read()
    #     # print(d)
    #     l = []
    #     test_case = yaml.load(d, Loader=Loader)
    #     core_test = test_case.get(name)
    #     if core_test != None:
    #         # print(core_test.keys())
    #         keys = core_test.keys()
    #         for key in keys:
    #             # print(core_test[key])
    #             for t in core_test[key]:
    #                 # print(key+'.'+t)
    #                 l.append(format(key+'.'+t))
    # return l

def match():
    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    need_to_fix_dic = {}
    passed_dic = {}
    recording = False
    l = []
    key = ""
    with open(OUTPUT_FILE, "r") as f:
        for line in f.readlines():
            line=ansi_escape.sub('',line)
            if line.startswith('[ RUN      ]') and not recording:
                recording = True
                l = []
                key = line[13:].split(' ')[0].strip()
                l.append(line)
            elif line.startswith('[       OK ]'):
                l.append(line)
                recording = False
                passed_dic[key] = l
                l = []
            elif line.startswith('[  FAILED  ]'):
                recording = False
                l.append(line)
                need_to_fix_dic[key] = l
                l = []
            elif line.startswith('[ RUN      ]') and recording:
                need_to_fix_dic[key] = l
                key = line[13:].split(' ')[0].strip()
                l =[]
                l.append(line)
            elif line.startswith("panicked") and recording == True:
                recording = False
                l.append(line)
                need_to_fix_dic[key] = l
                l = []
            elif line.startswith("ASSERT FAILED") and recording == True:
                recording = False
                l.append(line)
                need_to_fix_dic[key] = l
                l = []
            elif line.startswith("qemu-system-x86_64") and recording == True:
                recording = False
                need_to_fix_dic[key] = l
                l = []
            elif line.startswith("BdsDxe") and recording == True:
                recording = False
                need_to_fix_dic[key] = l
                l = []
            elif recording == True:
                l.append(line)


    with open(STATISTIC_BAD_FILE, "w") as f:
        index = 0
        for k in need_to_fix_dic.keys() :
            index += 1
            k = k.strip()
            f.write("{0} ============================== {1} ==============================\n".format(index,k))
            f.writelines(need_to_fix_dic[k])
            f.write("============================== End ==============================\n")
            f.write("\n\n")

    with open(STATISTIC_GOOD_FILE, "w") as f:
        index = 0
        for k in passed_dic.keys() :
            index += 1
            f.write("{0} ============================== {1} ==============================\n".format(index,k))
            f.writelines(passed_dic[k])
            f.write("============================== End ==============================\n")
            f.write("\n\n")

                 

# os.chdir(PWD)

subprocess.run("git checkout " + branch,shell=True,cwd=BASE + "/warehouse/" + "zCore" + "_realm/" + user + "/" + "zCore")
lines = []

lines = perpare_data("core-test")

# with open(ALL_CASES_FILE, "r") as f:
#     lines = f.readlines()

with open(RESULT_FILE, "w") as f:
    f.write('('+branch+') 测例统计:\n')

with open(OUTPUT_FILE, "w") as f:
    pass

subprocess.run("make build-parallel-test mode=release",shell=True,cwd=BASE+"/warehouse/" + "zCore" + "_realm/" + user + "/" + "zCore" + "/zCore")

os.chdir(BASE + "/warehouse/" + "zCore" + "_realm/" + user + "/" + "zCore")
start = time.time() 
print("开始计时")

with open(OUTPUT_FILE, "a") as f:
    for (n,line) in enumerate(lines):
        if line.startswith('#') or line.startswith('\n'):
            continue
        line = line.strip()
        running(n,line,f)


end = time.time()
os.chdir(BASE)
print('用时--times{:.3f}'.format(end-start))

match()

subprocess.run("python3 analysis.py " + user + " " + branch,shell=True,cwd=BASE + "/warehouse/" + "zCore" + "_realm/" + "scripts")
# os.system('python3 statistics.py '+user + " " +branch)