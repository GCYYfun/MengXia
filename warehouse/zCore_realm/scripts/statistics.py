import re

BASE = "/home/own/MengXia"
OUTPUT_FILE = BASE + "/warehouse/" + "zCore" + "_realm/" + "config/" + "output.txt"
STATISTIC_BAD_FILE = BASE + "/warehouse/" + "zCore" + "_realm/" + "config/" + "test-statistic-bad.txt"
STATISTIC_GOOD_FILE = BASE + "/warehouse/" + "zCore" + "_realm/" + "config/" + "test-statistic-good.txt"


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
            elif line.startswith('[       OK ]') and line.endswith(')\n'):
                l.append(line)
                recording = False
                passed_dic[key] = l
                l = []
            elif line.startswith('[  FAILED  ]') and line.endswith(')\n'):
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
                need_to_fix_dic[key] = l
                l = []
            elif recording == True:
                l.append(line)



    with open(STATISTIC_BAD_FILE, "w") as f:
        index = 0
        for k in need_to_fix_dic.keys() :
            index += 1
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

match()