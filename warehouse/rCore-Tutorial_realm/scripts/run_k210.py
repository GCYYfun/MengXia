import pexpect
import os
import sys
import subprocess
import time

subprocess.run("pwd")
user = sys.argv[1]
branch = sys.argv[2]

#===============File Config========================

BASE = "/home/own/work/MengXia"

LOGFILE = BASE + "/warehouse" + "/rCore-Tutorial" + "_realm/" + user + "/logfile/" + branch + "/k210" + "/logfile.txt"
RESULT = BASE + "/warehouse" + "/rCore-Tutorial" + "_realm/" + user + "/result/" + branch + "/k210" + "/result.txt"
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

    # 读取 文件 
    # 文件内容 测试 命令
    # lines = []
    # with open(CONFIG, "r") as f:
    #     lines = f.readlines()

    # logfile = open(LogFile,"wb")
    with open(RESULT,"w",encoding='utf-8',errors='ignore'):
        pass
    #     lines = f.readlines()
    # result = open(Result,"w",encoding='utf-8',errors='ignore')

    # 循环测试
        # 预期 测试结果 反馈 信息
    # with open(LOGFILE,"w",encoding="utf-8",errors="ignore") as fd:

        # child = pexpect.spawn("qemu-system-x86_64 -smp cores=4 -bios "+ BIOS_UEFI 
        #                         +" -drive format=raw,file=fat:rw:"+ EFI_System_Partition 
        #                         +" -serial mon:stdio -m 4G -device isa-debug-exit -drive format=qcow2,file="+FileSystem 
        #                         +" ,media=disk,cache=writeback,id=sfsimg,if=none -device ahci,id=ahci0 -device ide-drive,drive=sfsimg,bus=ahci0.0 -nographic",timeout=10)
    child = pexpect.spawn("make run BOARD=k210",timeout=30,encoding='utf-8')

    # child.delaybeforesend = 1
    # child.delayafterclose = 1 
    # child.delayafterterminate = 1 
    child.logfile = Tee(LOGFILE,"w")

    
    # child.sendline("\n")

    # name = str(num)+" "+line.split("/",3)[3].split(".")[0]

    index = child.expect(["密码：*",">>",pexpect.EOF,pexpect.TIMEOUT]) 
    if index == 0: 
        # with open(RESULT,"a",encoding='utf-8',errors='ignore') as f:
            # f.writelines("finished\n")
        child.sendline("0")
        child.expect(">>")
        child.sendline("hello_world")
        child.expect(">>")
        child.sendline("fantastic_text")
        child.expect(">>")
        with open(RESULT,"a",encoding='utf-8',errors='ignore') as f:
            f.writelines("Finish\n")
        print("Done!")
    elif index == 1:
        child.sendline("hello_world")
        child.expect(">>")
        child.sendline("fantastic_text")
        child.expect(">>")
        with open(RESULT,"a",encoding='utf-8',errors='ignore') as f:
            f.writelines("Finish\n")
        print("Done!")
    elif index == 2:
        with open(RESULT,"a",encoding='utf-8',errors='ignore') as f:
            f.writelines("EOF\n")
    elif index == 3:
        with open(RESULT,"a",encoding='utf-8',errors='ignore') as f:
            f.writelines("TIMEOUT\n")

os.chdir(BASE + "/warehouse/" + "rCore-Tutorial" + "_realm/" + user + "/" + "rCore-Tutorial")
subprocess.run("git checkout " + branch,shell=True)
main()
os.chdir(BASE)