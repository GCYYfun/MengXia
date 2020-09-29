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


user = sys.argv[1]
branch = sys.argv[2]
BASE = "/home/own/work/MengXia"

QEMU_RESULT_FILE = BASE + "/warehouse/" + "rCore-Tutorial" + "_realm/"  + user + "/result/" + branch + "/qemu" + "/result.txt"
QEMU_LOGFILE = BASE + "/warehouse/" + "rCore-Tutorial" + "_realm/"  + user + "/logfile/" + branch + "/qemu" + "/logfile.txt"

K210_RESULT_FILE = BASE + "/warehouse/" + "rCore-Tutorial" + "_realm/"  + user + "/result/" + branch + "/k210" + "/result.txt"
K210_LOGFILE = BASE + "/warehouse/" + "rCore-Tutorial" + "_realm/"  + user + "/logfile/" + branch + "/k210" + "/logfile.txt"
# ================

def send_mail():
    os.chdir(BASE + "/warehouse/" + "rCore" + "_realm/" + user + "/" + "rCore")
    resp = os.popen('git log --pretty=tformat:%h-%cn-%ce-%an-%ae -1').readline()
    porp = resp.strip().split('-')
    print(porp)
    sender = '734536637@qq.com'
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

    # PASSED = subprocess.run("grep PASSED " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()
    # FAILED = subprocess.run("grep FAILED " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()
    # PANICKED = subprocess.run("grep PANICKED " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()
    # TIMEOUT = subprocess.run("grep TIMEOUT " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()
    # TOTAL = subprocess.run("grep result " + RESULT_FILE + " | wc -l",shell=True,stdout=subprocess.PIPE,encoding="utf-8").stdout.strip()

    # print("通过率:", (float(PASSED)/float(TOTAL)) * 100 , "%")

    # print("不通过率:", ((float(FAILED)+float(PANICKED)+float(TIMEOUT))/float(TOTAL)) * 100 , "%")

    # print("超时率:", (float(TIMEOUT)/float(TOTAL)) * 100 , "%")

    # print("崩溃率:", (float(PANICKED)/float(TOTAL)) * 100 , "%")

    #邮件正文内容
    message.attach(
        MIMEText(
            '作者 ： ' + porp[3] + '\n' +
            'github 用户 ： ' + user + '\n' +
            '仓库 ： ' + 'rCore' + '\n' +
            '分支 ： ' + branch + '\n' +
            ' commit : ' + porp[0] +' 的libc测试结果 \n\n'+
            '\n\n  \n目前还没有对此具体的分析、仅显示统计 结果见result附件、 \n测试时间 ' +
            str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")), 'plain',
            'utf-8'))

    att1 = MIMEText(open(QEMU_RESULT_FILE, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att1["Content-Disposition"] = 'attachment; filename="qemu_result.txt"'
    message.attach(att1)

    att2 = MIMEText(open(QEMU_LOGFILE, 'rb').read(), 'base64', 'utf-8')
    att2["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att2["Content-Disposition"] = 'attachment; filename="qemu_logfile.txt"'
    message.attach(att2)

    att3 = MIMEText(open(K210_RESULT_FILE, 'rb').read(), 'base64', 'utf-8')
    att3["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att3["Content-Disposition"] = 'attachment; filename="k210_result.txt"'
    message.attach(att3)

    att4 = MIMEText(open(K210_LOGFILE, 'rb').read(), 'base64', 'utf-8')
    att4["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att4["Content-Disposition"] = 'attachment; filename="k210_logfile.txt"'
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
# print("统计分析...")
send_mail()
# print("分析完毕...")