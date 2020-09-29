import os
import sys
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

import subprocess

# ================
subprocess.run("pwd")
TEMP_DIFF = ""


user = sys.argv[1]
branch = sys.argv[2]
BASE = "/home/own/work/MengXia"
OUTPUT_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/logfile/" + branch + "/zircon" + "/output.txt"
RESULT_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/result/" + branch +  "/zircon" + "/test-result.txt"
LAST_RESULT_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/result/" + branch + "/zircon" + "/test-result-last.txt"
DIFF_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/diff/" + branch + "/zircon" + "/diff"
STATISTIC_BAD_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/help_info/" + branch + "/zircon" + "/test-statistic-bad.txt"
TEMP_FILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/diff/" + branch + "/zircon" + "/diff"

# 临时添加 有待改进 有历史 记录
LIBC_LOGFILE = BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/logfile/" + branch + "/linux" + "/libc_output.txt"
# ================

last_set = set()
curr_set = set()


def compare_diff(branch,resultA = LAST_RESULT_FILE ,resultB = RESULT_FILE):
    with open(resultA,'r') as last, open(resultB, 'r') as curr:

        for line in last.readlines():
            if line.startswith("["):
                last_set.add(line)
        for line in curr.readlines():
            if line.startswith("["):
                curr_set.add(line)

        with open(DIFF_FILE, 'w') as f:

            diff_set = curr_set - last_set
            if len(diff_set) == 0:
                f.write(" Current total : " + str(len(curr_set)) + " test cases \n There are all no change")
            else:
                for case in diff_set:
                    f.write("[更新]    " + case)
                f.write(" Current total : " + str(len(curr_set)) + " test cases \n New added : " +
                        str(len(curr_set) - len(last_set)) + "\n Change test cases : " +
                        str(len(diff_set)))

        TEMP_DIFF = TEMP_FILE + str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+".txt")
        subprocess.run("mv " + DIFF_FILE + " " + TEMP_DIFF,shell=True)
        return TEMP_DIFF


def send_mail(file_name):
    os.chdir(BASE + "/warehouse/" + "zCore" + "_realm/" + user + "/" + "zCore")
    resp = os.popen('git log --pretty=tformat:%h-%cn-%ce-%an-%ae -1').readline()
    porp = resp.strip().split('-')
    print(porp)
    sender = 'zcore_devinfo@163.com'
    mail_list = "zcore_info@groups.163.com"
    receivers = [mail_list]

    # if porp[1] == porp[3]:
    #     receivers.append(porp[2])
    # else:
    #     if porp[2].startswith("noreply@github.com"):
    #         print("noreply")
    #         receivers.append(porp[4])
    #     else:
    #         receivers.append(porp[2])
    #         receivers.append(porp[4])

    # receivers = [porp[2]]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    #创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = Header("zcore dev feedback", 'utf-8')
    message['To'] = Header(porp[3], 'utf-8')
    subject = '提交结果反馈'
    message['Subject'] = Header(subject, 'utf-8')

    PASSED = subprocess.run("grep PASSED " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()
    FAILED = subprocess.run("grep FAILED " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()
    PANICKED = subprocess.run("grep PANICKED " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()
    TIMEOUT = subprocess.run("grep TIMEOUT " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()
    TOTAL = subprocess.run("grep result " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()

    # print("通过率:", (float(PASSED)/float(TOTAL)) * 100 , "%")

    # print("不通过率:", ((float(FAILED)+float(PANICKED)+float(TIMEOUT))/float(TOTAL)) * 100 , "%")

    # print("超时率:", (float(TIMEOUT)/float(TOTAL)) * 100 , "%")

    # print("崩溃率:", (float(PANICKED)/float(TOTAL)) * 100 , "%")

    #邮件正文内容
    message.attach(
        MIMEText(
            '作者 ： ' + porp[3] + '\n' +
            'github 用户 ： ' + user + '\n' +
            '仓库 ： ' + 'zCore' + '\n' +
            '分支 ： ' + branch + '\n' +
            ' commit : ' + porp[0] +' 的测试结果 \n\n'+format(("通过率 : " + str((float(PASSED)/float(TOTAL)) * 100) + "%"))+'\n'+format("不通过率 : " + str(((float(FAILED)+float(PANICKED)+float(TIMEOUT))/float(TOTAL)) * 100) + "%")+'\n'+format("超时率 : " + str((float(TIMEOUT)/float(TOTAL)) * 100) + "%")+'\n'+("崩溃率 : " + str((float(PANICKED)/float(TOTAL)) * 100) + "%")+'\n'+'\n\n  \n与上一次比较的变化内容见diff附件(没有diff则为第一次提交、无上次可比较信息)、\n全部测试结果见result附件、\n详细错误信息见info附件、 \n测试时间 ' +
            str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")), 'plain',
            'utf-8'))

    att1 = MIMEText(open(RESULT_FILE, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att1["Content-Disposition"] = 'attachment; filename="result.txt"'
    message.attach(att1)

    if file_name != "no":
        att2 = MIMEText(open(file_name, 'rb').read(), 'base64', 'utf-8')
        att2["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att2["Content-Disposition"] = 'attachment; filename="diff.txt"'
        message.attach(att2)
    
    att3 = MIMEText(open(STATISTIC_BAD_FILE, 'rb').read(), 'base64', 'utf-8')
    att3["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att3["Content-Disposition"] = 'attachment; filename="info.txt"'
    message.attach(att3)

    if os.path.exists(LIBC_LOGFILE):
        att4 = MIMEText(open(LIBC_LOGFILE, 'rb').read(), 'base64', 'utf-8')
        att4["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att4["Content-Disposition"] = 'attachment; filename="libc_info.txt"'
        message.attach(att4)    

    # 第三方 SMTP 服务
    # QQ

    # mail_host = "smtp.qq.com"  #设置服务器
    # mail_user = "734536637@qq.com"  #用户名
    # mail_pass = "srjduzcigxgqbeha"  #口令

    # 网易
    # mail_host='smtp.163.com'
    # mail_user='cx734536637@163.com'    #用户名
    # mail_pass='MSJHKKZZOYNLQRWN'   #口令
    # 网易 MSJHKKZZOYNLQRWN

    mail_host = 'smtp.163.com'
    mail_user = 'zcore_devinfo@163.com'    #用户名
    mail_pass = 'DWCJDLLPXOXPEOPA'

    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
    smtpObj.login(mail_user, mail_pass)

    try:
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

    smtpObj.quit()
    os.chdir(BASE)


# os.system("pwd")
# branch = sys.argv[1]
print("统计分析...")
if os.path.exists(LAST_RESULT_FILE):
    diff_name = compare_diff(branch)
    subprocess.run("cp " + RESULT_FILE + " " + LAST_RESULT_FILE,shell=True)
    subprocess.run('cp ' + RESULT_FILE + " " + BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/result/" + branch + "/test-result" + str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")) + ".txt",shell=True)
    print(diff_name)
    print("暂时 关闭 邮件 发送")
    send_mail(diff_name)
else:
    subprocess.run("cp " + RESULT_FILE + " " + LAST_RESULT_FILE,shell=True)
    subprocess.run('cp ' + RESULT_FILE + " " + BASE + "/warehouse/" + "zCore" + "_realm/"  + user + "/result/" + branch + "/test-result" + str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")) + ".txt",shell=True)
    print("暂时 关闭 邮件 发送")
    send_mail("no")

print("分析完毕...")
