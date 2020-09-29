import pexpect
import os
import sys
import subprocess
import time

subprocess.run("pwd")
user = sys.argv[1]
branch = sys.argv[2]

#===============Must Config========================

BASE = "/home/own/MengXia"

OVMF = "rboot/OVMF.fd"
ESP = "kernel/target/x86_64/release/esp"
IMG = "user/build/x86_64.qcow2"

LogFile = BASE + "/warehouse" + "/rCore" + "_realm/" + user + "/logfile/" + branch + "/logfile.txt"
Result = BASE + "/warehouse" + "/rCore" + "_realm/" + user + "/result/" + branch + "/result.txt"
Config = BASE + "/warehouse" + "/rCore" + "_realm/" + "config" + "/libc_test.txt"

#==============================================

# qeme 的 参数

args=["-smp","cores=4",
        "-drive","if=pflash,format=raw,readonly,file=" + OVMF,
        "-drive","format=raw,file=fat:rw:" + ESP,
        "-serial","mon:stdio","-m","4G",
        "-device","isa-debug-exit",
        "-drive","format=qcow2,file=" + IMG + ",media=disk,cache=writeback,id=sfsimg,if=none",
        "-device","ahci,id=ahci0",
        "-device","ide-drive,drive=sfsimg,bus=ahci0.0",
        "-accel","kvm",
        "-cpu","host",
        "-nographic"
        ]

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
    lines = []
    with open(Config, "r") as f:
        lines = f.readlines()

    # logfile = open(LogFile,"wb")
    with open(Result,"w",encoding='utf-8',errors='ignore'):
        pass
    #     lines = f.readlines()
    # result = open(Result,"w",encoding='utf-8',errors='ignore')

    num = 0
    # 循环测试
        # 预期 测试结果 反馈 信息
    with open(LogFile,"w",encoding="utf-8",errors="ignore") as fd:


        for line in lines:

            if line.startswith("#") or line == '\n':
                continue

            num+=1
            # child = pexpect.spawn("qemu-system-x86_64 -smp cores=4 -bios "+ BIOS_UEFI 
            #                         +" -drive format=raw,file=fat:rw:"+ EFI_System_Partition 
            #                         +" -serial mon:stdio -m 4G -device isa-debug-exit -drive format=qcow2,file="+FileSystem 
            #                         +" ,media=disk,cache=writeback,id=sfsimg,if=none -device ahci,id=ahci0 -device ide-drive,drive=sfsimg,bus=ahci0.0 -nographic",timeout=10)
            child = pexpect.spawn("qemu-system-x86_64",args,timeout=10,encoding='utf-8')

            child.delaybeforesend = 0.1
            child.delayafterclose = 0.2
            child.delayafterterminate = 0.1
            child.logfile = fd

            child.expect("/ # ")
            child.sendline("cd libc-test")

            child.expect("/libc-test # ")
            child.sendline(line)

            name = str(num)+" "+line.split("/",3)[3].split(".")[0]

            index = child.expect(["successed","failed",pexpect.EOF,pexpect.TIMEOUT,"/libc-test #","Hangup","=== BEGIN rCore stack trace ==="]) 
            if index == 0: 
                with open(Result,"a",encoding='utf-8',errors='ignore') as f:
                    f.writelines(name+" successed\n")
            elif index == 1:
                with open(Result,"a",encoding='utf-8',errors='ignore') as f:
                    f.writelines(name+" failed\n")
            elif index == 2:
                with open(Result,"a",encoding='utf-8',errors='ignore') as f:
                    f.writelines(name+" EOF\n")
            elif index == 3:
                with open(Result,"a",encoding='utf-8',errors='ignore') as f:
                    f.writelines(name+" 10s_timeout\n")
            elif index == 4:
                with open(Result,"a",encoding='utf-8',errors='ignore') as f:
                    f.writelines(name+" successed\n")
            elif index == 5:
                with open(Result,"a",encoding='utf-8',errors='ignore') as f:
                    f.writelines(name+" hangup\n")
            elif index == 6:
                with open(Result,"a",encoding='utf-8',errors='ignore') as f:
                    f.writelines(name+" panic\n")
    # child = pexpect.spawn("qemu-system-x86_64",args,timeout=100,encoding='utf-8',echo=True)
    # child.logfile = Tee(LogFile,"w")
    # child.delayafterclose = 2

    # child.expect("/ # ")
    # child.sendline("cd libc-test")

    # child.expect("/libc-test # ")
    # child.sendline("sh success.sh")
    # child.expect(pexpect.EOF)
    

# if __name__ == "__main__":

os.chdir(BASE + "/warehouse/" + "rCore" + "_realm/" + user + "/" + "rCore")
subprocess.run("git checkout " + branch,shell=True)

main()
os.chdir(BASE)
