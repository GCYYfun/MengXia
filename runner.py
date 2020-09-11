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
    os.chdir(PWD)  # 设置工作目录
    # 定时 读取 redis
    # wait_for_test = take_need_test_branch()

    # running(wait_for_test)
    start_runner()

    ## 开启监听
    while True:
        schedule.run_pending()


def run_core_test(repo, branch):

    # 过滤 这个 仓库 的 这个 分支 是否 执行

    user = repo.split(":")[0]
    name = repo.split(":")[1]
    subprocess.run("git checkout " + branch,shell=True,cwd="warehouse/" + name + "_realm/" + user + "/" + name)
    # switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name)
    # os.system("git checkout " + branch)

    print(user, " - ", name, "coretest开始运行")
    ## 进入 仓库
    # os.chdir(PWD)
    # os.chdir("./warehouse/" + repo.name + "_realm/" + repo.user + "/" +
    #          repo.name + "/zCore")
    # ## build
    # switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name +
    #            "/zCore")
    # os.system("make build-parallel-test mode=release")

    # subprocess.run("make build-parallel-test mode=release",shell=True,cwd="warehouse/" + name + "_realm/" + user + "/" + name + "/zCore")
    subprocess.run("python3 core-tests.py",shell=True,cwd="warehouse/" + name + "_realm/" + user + "/" + name + "/scripts")
    # subprocess.run("python3 core-tests.py",shell=True,cwd="warehouse/" + name + "_realm/" + user + "/" + name + "/scripts")
    
    # os.chdir(PWD)
    # ## 指定当前工作目录
    # switch_dir("./warehouse/" + name + "_realm/" + user)
    # ## 执行测试
    # os.system("python3 ../parallel-test.py " + branch)
    
    # subprocess.run("python3 parallel-test.py " + branch,shell=True,cwd="warehouse/" + name + "_realm/scripts")
    
    # os.chdir(PWD)
    # switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name +
    #            "/zCore")
    # os.system("make clean")
    subprocess.run("make clean",shell=True,cwd="warehouse/" + name + "_realm/" + user + "/" + name + "/zCore")
    print(user, " - ", name, "coretest运行结束")
    # os.chdir(PWD)

    pass


def run_libc_test(repo, branch):

    # 过滤 这个 仓库 的 这个 分支 是否 执行

    user = repo.split(":")[0]
    name = repo.split(":")[1]

    ## 进入 仓库
    print(user, " - ", name, "libc开始运行")
    subprocess.run("git checkout " + branch,shell=True,cwd="warehouse/" + name + "_realm/" + user + "/" + name)
    # switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name)
    ## build
    subprocess.run("make rootfs && make libc-test",shell=True,cwd="warehouse/" + name + "_realm/" + user + "/" + name)
    # os.system("make rootfs && make libc-test")
    ## 指定当前工作目录
    # switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name +
    #            "/scripts")
    ## 执行测试
    subprocess.run("python3 parallel-test.py " + branch,shell=True,cwd="warehouse/" + name + "_realm/" + user + "/" + name + "/scripts")
    # os.system("python3 libc-tests.py")
    # switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name +
    #            "/zCore")

    # os.system("make clean")
    print(user, " - ", name, "libc运行结束")
    # os.chdir(PWD)


def running():
    # 设置 占用

    # temp
    wait_for_test = take_need_test_branch()

    with open("./config/test_spec.yaml", "r") as f:
        d = f.read()
        print(d)
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
                print("指定 测试 ")
                for i in fns:
                    print(i)
                    if i == "core_test":
                        print("运行 coretest")
                        run_core_test(r, b)
                    elif i == "libc_test":
                        print("运行 libctest")
                        run_libc_test(r, b)
            else:
                # run_core_test(r, b)
                # run_libc_test(r, b)
                print(repo_name,":",b,"无指定 测试")

            
        redisManager.finish_running(r)
        print("运行 完毕 清除 redis")


def start_runner():
    schedule.every(10).seconds.do(running)


def take_need_test_branch():
    need_test = redisManager.take_need_test()
    return need_test


# def switch_dir(path):
#     print("切换 工作 目录 ----->")
#     os.chdir(PWD)
#     print("切换前:" + str(os.system("pwd")))
#     os.chdir(path)
#     print("切换后:" + str(os.system("pwd")))


if __name__ == '__main__':
    main()
