# 轮询 读取 信息 进行 更新

# 更新 时 标记 正在 工作

# （高级） 可配置 和 指定 什么 分支  需要 执行 的 测试集  需要 一个 文件
# 默认全部

# 系统
## ====================
import os
import sys
## ====================

# Redis
## ====================
import ownlib.redis_manager as rdm
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
    wait_for_test = take_need_test_branch()

    running(wait_for_test)
    # start_runner()

    ## 开启监听
    # while True:
    #     schedule.run_pending()


def run_core_test(repo, branch):
    user = repo.split(":")[0]
    name = repo.split(":")[1]
    switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name)
    os.system("git checkout " + branch)

    print(user, " - ", name, "coretest开始运行")
    ## 进入 仓库
    # os.chdir(PWD)
    # os.chdir("./warehouse/" + repo.name + "_realm/" + repo.user + "/" +
    #          repo.name + "/zCore")
    # ## build
    switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name +
               "/zCore")
    os.system("make build-parallel-test mode=release")
    # os.chdir(PWD)
    # ## 指定当前工作目录
    switch_dir("./warehouse/" + name + "_realm/" + user)
    # ## 执行测试
    # os.system("python3 ../parallel-test.py " + branch)
    # os.chdir(PWD)
    switch_dir("./warehouse/" + name + "_realm/" + user + "/" + name +
               "/zCore")
    os.system("make clean")
    print(repo.user, " - ", repo.name, "coretest运行结束")
    os.chdir(PWD)

    pass


def run_libc_test(repo, branch):
    pass


def running(wait_for_test):
    # 设置 占用
    for k in wait_for_test.keys():
        redisManager.start_running(k)
        print("待测试")
        print(k, ":", wait_for_test[k])
        for t in wait_for_test[k]:

            # 进入 仓库 进入 分支 执行 测试
            run_core_test(k, t)
            # run_core_test()
            # run_core_test()
            # run_core_test()
            # run_core_test()
            print(t)
        redisManager.finish_running(k)


def start_runner():
    schedule.every(10).seconds.do(take_need_test_branch)


def take_need_test_branch():
    need_test = redisManager.take_need_test()
    return need_test


def switch_dir(path):
    print("切换 工作 目录 ----->")
    os.chdir(PWD)
    print("切换前:" + str(os.system("pwd")))
    os.chdir(path)
    print("切换后:" + str(os.system("pwd")))


if __name__ == '__main__':
    main()
