# 系统
## ====================
import os
## ====================

# 定时
## ====================
import schedule
## ====================

# 网络请求
## ====================
import requests
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

# Redis
## ====================
import ownlib.redis_manager as rdm
## ====================

# Redis
## ====================
import ownlib.repo_manager as rm
## ====================

# Config
## ====================
ALREADY_EXIST_REPO = "config/already_clone.yaml"
REPO_INFO = "warehouse/zCore_realm/config"
PWD = "/home/own/MengXia"
## ====================

## redis实例
redisManager = rdm.RedisManager()
## repos实例
repoManager = rm.RepoManager()


def clone_fn(repo):

    # 1.  设置 工作 目录
    print("切换 工作 目录 ----->")
    print("切换前:" + str(os.system("pwd")))
    os.chdir("./warehouse/" + repo.name + "_realm/" + repo.user)
    print("切换后:" + str(os.system("pwd")))
    # 2.  clone 仓库
    try:
        print("开始 clone")
        # os.system("git clone "+repo.url+" --recursive --depth 1")
        os.system("git clone " + repo.url + " --recursive")
    except:
        print("clone 失败 ，重置工作目录 退出 clone")
        os.chdir(PWD)
        return
    #     clone 完成 标记
    res = redisManager.add_exist_repo(repo.url)
    if res == 1:
        print("添加成功")
    else:
        print("添加失败，已存在")

    # 3. 探测分支
    # print("分支获取")
    # try:
    #     header = {'Accept': 'application/vnd.github.v3+json'}
    #     url = 'https://api.github.com/repos/' + repo.user + '/' + repo.name + '/branches'
    #     res = requests.get(url=url, headers=header)
    #     json_branches = res.text
    # except:
    #     print("请求失败")
    #     os.chdir(PWD)
    #     return
    # chech_branch_json_validity(json_branches)
    # print("请求成功")
    # #    转化 json
    # branches = json.loads(json_branches)

    # print("准备 branch dir")
    # for branche in branches:
    #     prepare_branch_dir(branche["name"])
    # print("准备 完毕")

    branches = request_repo_branches(repo)
    #    记录分支
    redisManager.save_branch_info(repo, branches)
    os.chdir(PWD)


def update_fn(repo):
    print("Update")
    print("切换 工作 目录 ----->")
    print("切换前:" + str(os.system("pwd")))
    os.chdir("./warehouse/" + repo.name + "_realm/" + repo.user)
    print("切换后:" + str(os.system("pwd")))
    branches = request_repo_branches(repo)
    compare_branch_info(repo, branches)

    os.chdir(PWD)
    # try:
    #     header = {'Accept': 'application/vnd.github.v3+json'}
    #     url = 'https://api.github.com/repos/' + repo.user + '/' + repo.name + '/branches'
    #     res = requests.get(url=url, headers=header)
    #     json_branches = res.text
    # except:
    #     print("请求失败")
    #     os.chdir(PWD)
    #     return
    # # 检测 合法性
    # if not chech_branch_json_validity(json_branches):
    #     return

    # print("请求成功")
    # 1. 获取 branch 信息
    # 2. 解析 branch 信息
    # 3. 依据 新 branch 信息 和 本地 branch 信息 做对比
    # 4. 对 变化的 branch 进入 相对应的 branch 进行 更新
    # 5. 标记 此 branch 需要 测试

    pass


def register_watch(repo, clone_fn, update_fn):
    if repo.url in repoManager.already_exist_repo:
        print(repo.user + ":" + repo.name + " repo存在 开始 监测更新")
        schedule.every(10).seconds.do(update_fn, repo)
    else:
        print(repo.user + ":" + repo.name + " repo不存在 clone并 开始 监测更新")
        if os.path.exists("warehouse/" + repo.name + "_realm/" + repo.user +
                          "/" + repo.name):
            os.system("rm -rf warehouse/" + repo.name + "_realm/" + repo.user +
                      "/" + repo.name)
        os.chdir(PWD)
        clone_fn(repo)
        schedule.every(1).minutes.do(update_fn, repo)


def main():
    os.chdir(PWD)  # 设置工作目录
    for repo in repoManager.repos:
        prepare_dir(repo)
        register_watch(repo, clone_fn, update_fn)

    ## 开启监听
    while True:
        schedule.run_pending()


# ================== 仓库 区


def prepare_dir(repo):
    # 幂等性
    print("准备 文件目录")
    os.system("mkdir -p warehouse/" + repo.name + "_realm/config")
    os.system("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user +
              "/config")
    # os.system("cp config/all-test-cases.txt " + repo.user +
    #           "/config/all-test-cases.txt")
    os.system("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user +
              "/diff")
    os.system("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user +
              "/result")


def prepare_branch_dir(branch):
    os.system("mkdir -p config/" + branch)
    os.system("mkdir -p diff/" + branch)
    os.system("mkdir -p result/" + branch)


def request_repo_branches(repo):
    try:
        header = {'Accept': 'application/vnd.github.v3+json'}
        url = 'https://api.github.com/repos/' + repo.user + '/' + repo.name + '/branches'
        res = requests.get(url=url, headers=header)
        json_branches = res.text
    except:
        print("请求失败")
        os.chdir(PWD)
        return []
    chech_branch_json_validity(json_branches)
    print("请求成功")
    #    转化 json
    branches = json.loads(json_branches)

    print("准备 branch dir")
    for branche in branches:
        prepare_branch_dir(branche["name"])
    print("准备 完毕")
    return branches


def chech_branch_json_validity(json_branches):
    #    边界 设置
    if len(json_branches) == 0:
        print("请求失败")
        os.chdir(PWD)
        return False
    if json_branches.startswith('{'):
        print("值不对 {")
        os.chdir(PWD)
        return False
    return True


def compare_branch_info(repo, curr_branches):
    print(curr_branches)
    curr = set()
    for b in curr_branches:
        curr.add(str(b))
        
    last = redisManager.read_branch_info(repo)
    print("last")
    print(last)
    
    diff = curr - last
    print("diff")
    print(diff)
    pass


if __name__ == '__main__':
    main()
