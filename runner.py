# 轮询 读取 信息 进行 更新

# 更新 时 标记 正在 工作

# （高级） 可配置 和 指定 什么 分支  需要 执行 的 测试集  需要 一个 文件
# 默认全部

# 系统
## ====================
import os
import sys
import subprocess
## ====================

# Redis
## ====================
import ownlib.redis_manager as rdm
## ====================

# 解析
## ====================
import json
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper
## ====================

# 定时
## ====================
import schedule
## ====================

PWD = sys.path[0]

redisManager = rdm.RedisManager()


def main():
    print("PWD ", PWD)
    os.chdir(PWD)  # 设置工作目录

    start_runner()

    ## 开启监听
    while True:
        schedule.run_pending()


def run_core_test(repo, branch):

    # 过滤 这个 仓库 的 这个 分支 是否 执行

    user = repo.split(":")[0]
    name = repo.split(":")[1]

    print(user, " - ", name, "coretest开始运行")

    subprocess.run("python3 core_test.py " + user + " " + branch,
                   shell=True,
                   cwd="warehouse/" + name + "_realm/" + "scripts")

    subprocess.run("make clean",
                   shell=True,
                   cwd="warehouse/" + name + "_realm/" + user + "/" + name +
                   "/zCore")
    print(user, " - ", name, "coretest运行结束")


def run_libc_test(repo, branch):

    # 过滤 这个 仓库 的 这个 分支 是否 执行

    user = repo.split(":")[0]
    name = repo.split(":")[1]

    ## 进入 仓库
    print(user, " - ", name, "libc开始运行")
    ## build
    ## 执行测试
    subprocess.run("python3 libc_test.py " + user + " " + branch,
                   shell=True,
                   cwd="warehouse/" + name + "_realm/" + "scripts")

    print(user, " - ", name, "libc运行结束")


def run_rcore_libc(repo, branch):
    user = repo.split(":")[0]
    name = repo.split(":")[1]

    print(user, " - ", name, "libc开始运行")

    # build

    subprocess.run("git checkout " + branch,
                   shell=True,
                   cwd="./warehouse/" + name + "_realm/" + user + "/" + name)
    # subprocess.run("make sfsimg PREBUILT=1 ARCH=x86_64",shell=True,cwd="./warehouse/" + name + "_realm/" + user + "/" + name + "/user")
    # subprocess.run("make build ARCH=x86_64",shell=True,cwd="./warehouse/" + name + "_realm/" + user + "/" + name + "/kernel")

    # run
    subprocess.run("python3 libc_test.py " + user + " " + branch,
                   shell=True,
                   cwd="warehouse/" + name + "_realm/" + "scripts")

    print(user, " - ", name, "libc运行结束")


def run_qemu(repo, branch):
    user = repo.split(":")[0]
    name = repo.split(":")[1]

    print(user, " - ", name, "qemu开始运行")

    # build
    # run
    subprocess.run("python3 run_qemu.py " + user + " " + branch,
                   shell=True,
                   cwd="./warehouse/" + name + "_realm/" + "scripts")

    print(user, " - ", name, "qemu运行结束")


def run_k210(repo, branch):
    user = repo.split(":")[0]
    name = repo.split(":")[1]

    print(user, " - ", name, "k210开始运行")

    # build
    # run
    subprocess.run("python3 run_k210.py " + user + " " + branch,
                   shell=True,
                   cwd="./warehouse/" + name + "_realm/" + "scripts")

    print(user, " - ", name, "k210运行结束")


def running():
    # 设置 占用

    # temp
    wait_for_test = take_need_test_branch()

    if len(wait_for_test) != 0:
        with open("./config/test_spec.yaml", "r") as f:
            d = f.read()
            test_config = yaml.load(d, Loader=Loader)

        for r in wait_for_test.keys():
            redisManager.start_running(r)
            repo_name = r.split(":")[1]

            print("待测试")
            print(r, ":", wait_for_test[r])
            for b in wait_for_test[r]:
                try:
                    fns = test_config.get(repo_name).get(b)
                except:
                    fns = None
                # 进入 仓库 进入 分支 执行 测试
                if fns != None:
                    print("指定 测试 ", fns)
                    for i in fns:
                        print(i)
                        if repo_name == "zCore":
                            if i == "core_test":
                                print("运行 coretest")
                                run_core_test(r, b)
                            elif i == "libc_test":
                                print("运行 libctest")
                                run_libc_test(r, b)
                        elif repo_name == "rCore":
                            if i == "libc_test":
                                print("运行 libctest")
                                print("暂时 有问题")
                                # run_rcore_libc(r, b)
                        elif repo_name == "rCore-Tutorial":
                            if i == "qemu":
                                print("运行 qemu_run")
                                run_qemu(r, b)
                            elif i == "k210":
                                print("运行 k210")
                                run_k210(r, b)
                else:
                    if repo_name == "zCore":
                        run_core_test(r, b)
                        # run_libc_test(r, b)；
                    print(repo_name, ":", b, "非指定分支 不进行测试")
        redisManager.finish_running(r)
        print("运行 完毕 清除 redis")


def start_runner():
    schedule.every(1).minutes.do(running)


def take_need_test_branch():
    need_test = redisManager.take_need_test()
    return need_test


if __name__ == '__main__':
    main()
