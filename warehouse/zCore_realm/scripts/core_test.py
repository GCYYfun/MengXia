# 解析
## ====================
import json
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper
## ====================
import pexpect
import subprocess
import os

PWD = "/home/own/MengXia"

LOGFILE_FILE = PWD + "/warehouse/zCore_realm/GCYYfun/logfile/master/logfile"

RESULT_FILE = PWD + "/warehouse/zCore_realm/GCYYfun/result/master/result"

def running(test_list):
    os.chdir("warehouse/" + "zCore" + "_realm/" + "GCYYfun" + "/" + "zCore" + "/zCore")
    subprocess.run("make build-parallel-test mode=release",shell=True,cwd=PWD+"/warehouse/" + "zCore" + "_realm/" + "GCYYfun" + "/" + "zCore" + "/zCore")
    with open(LOGFILE_FILE, "w") as f:
        pass
    with open(LOGFILE_FILE, "a") as log:
        for i,t in enumerate(test_list):
            child = pexpect.spawn("make test mode=release accel=1 test_filter='"+t+"'",timeout=10,encoding='utf-8')
            
            child.logfile = log
            index = child.expect([
                'PASSED', 'FAILED', 'panicked', pexpect.EOF, pexpect.TIMEOUT,
                'Running 0 test from 0 test case'
            ])
            result = ['PASSED', 'FAILED', 'PANICKED', 'EOF', 'TIMEOUT',
                    'UNKNOWN'][index]
            print('[result]    ' + str(i) + '    ' + t + '    ' + result)
            with open(RESULT_FILE, "a") as f:
                f.write('[result]    ' + str(i) + '    ' + t + '    ' +
                        result + '\n')
    pass

def perpare_data(name):
    with open("./config/test_case.yaml", "r") as f:
        d = f.read()
        # print(d)
        l = []
        test_case = yaml.load(d, Loader=Loader)
        core_test = test_case.get(name)
        if core_test != None:
            # print(core_test.keys())
            keys = core_test.keys()
            for key in keys:
                # print(core_test[key])
                for t in core_test[key]:
                    # print(key+'.'+t)
                    l.append(format(key+'.'+t))
    return l
                    

def main():
    os.chdir(PWD)
    core_test = perpare_data("core-test")
    running(core_test)
    os.chdir(PWD)
    pass

if __name__=="__main__":
    main()