# 系统
## ====================
import os
import subprocess
import sys
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

PWD = sys.path[0]


def clone_fn(repo):

    # 1.  设置 工作 目录
    print("======================================")
    print("repo clone ", repo.user, " - ", repo.name)
    print("======================================")
    # print("切换 工作 目录 ----->")
    # os.chdir(PWD)
    # print("切换前:" + str(os.system("pwd")))
    # os.chdir("./warehouse/" + repo.name + "_realm/" + repo.user)
    # print("切换后:" + str(os.system("pwd")))
    # switch_dir("./warehouse/" + repo.name + "_realm/" + repo.user)
    # 2.  clone 仓库
    try:
        print("开始 clone")
        # os.system("git clone "+repo.url+" --recursive --depth 1")
        # os.system("git clone " + repo.url + " --recursive")
        subprocess.run("git clone " + repo.url + " --recursive",shell=True,check=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user)
    except:
        subprocess.run("rm -rf warehouse/" + repo.name + "_realm/" + repo.user + "/" + repo.name,shell=True)
        print("clone 失败 ，重置工作目录 退出 clone")

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
    # os.chdir(PWD)


def update_fn(repo):
    if not check_for_update_available(repo):
        return
    print("======================================")
    print("repo update ", repo.user, " - ", repo.name)
    print("======================================")

    # 请求 仓库 分支 信息
    branches = request_repo_branches(repo)
    # 对比 与 本地 的 情况 返回 变更的 分支
    need_branches = compare_branch_info(repo, branches)
    if len(need_branches) != 0:
        update_branch(repo, need_branches)
        mark_to_test(repo, need_branches)
        update_branch_info(repo, branches)
    # os.chdir(PWD)
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


def register_watch(repo, clone_fn, update_fn):
    if repo.url in repoManager.already_exist_repo:
        print(repo.user + ":" + repo.name + " repo存在 开始 监测更新")
        schedule.every(10).seconds.do(update_fn, repo)
    else:
        print(repo.user + ":" + repo.name + " repo不存在 clone并 开始 监测更新")
        # if os.path.exists("warehouse/" + repo.name + "_realm/" + repo.user +
        #                   "/" + repo.name):
        #     os.system("rm -rf warehouse/" + repo.name + "_realm/" + repo.user +
        #               "/" + repo.name)
        # os.chdir(PWD)
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
    subprocess.run("mkdir -p warehouse/" + repo.name + "_realm/config",shell=True)
    subprocess.run("mkdir -p warehouse/" + repo.name + "_realm/scripts",shell=True)
    subprocess.run("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user + "/config",shell=True)
    subprocess.run("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user + "/diff",shell=True)
    subprocess.run("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user + "/result",shell=True)
    subprocess.run("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user + "/logfile",shell=True)
    subprocess.run("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user + "/help_info",shell=True)
    
    # os.system("mkdir -p warehouse/" + repo.name + "_realm/config")
    # os.system("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user +
    #           "/config")
    # # os.system("cp config/all-test-cases.txt " + repo.user +
    # #           "/config/all-test-cases.txt")
    # os.system("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user +
    #           "/diff")
    # os.system("mkdir -p warehouse/" + repo.name + "_realm/" + repo.user +
    #           "/result")


def prepare_branch_dir(branch,repo):
    
    subprocess.run("mkdir -p config/" + branch,shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user)
    subprocess.run("mkdir -p diff/" + branch,shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user)
    subprocess.run("mkdir -p result/" + branch,shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user)
    subprocess.run("mkdir -p logfile/" + branch,shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user)
    subprocess.run("mkdir -p help_info/" + branch,shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user)
    # os.system("mkdir -p config/" + branch)
    # os.system("mkdir -p diff/" + branch)
    # os.system("mkdir -p result/" + branch)


def request_repo_branches(repo):
    try:
        header = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token fa5b00ae8df79e2f97b0017d4b22cd49245fa8ad '
        }

        url = 'https://api.github.com/repos/' + repo.user + '/' + repo.name + '/branches'
        res = requests.get(url=url, headers=header)
        json_branches = res.text
    except:
        print("请求失败")
        # os.chdir(PWD)
        return []
    chech_branch_json_validity(json_branches)
    print("请求成功")
    #    转化 json
    branches = json.loads(json_branches)

    # switch_dir("./warehouse/" + repo.name + "_realm/" + repo.user)
    print("准备 branch dir")
    for branche in branches:
        prepare_branch_dir(branche["name"],repo)
    print("准备 完毕")
    branches_list = convert_string_list(branches)
    return branches_list


def chech_branch_json_validity(json_branches):
    #    边界 设置
    if len(json_branches) == 0:
        print("请求失败")
        # os.chdir(PWD)
        return False
    if json_branches.startswith('{'):
        print("值不对 {")
        # os.chdir(PWD)
        return False
    return True


def compare_branch_info(repo, curr_branches):
    res = []
    # print(curr_branches)
    if len(curr_branches) == 0:
        return res
    print("比较 分支 信息")
    # print("当前远程 仓库 上 的 分支信息 ")
    curr = set()
    for b in curr_branches:
        curr.add(str(b).replace("'", "\""))
    # print("curr")
    # print(curr)

    last = redisManager.read_branch_info(repo)
    # print("last")
    # print(last)

    if len(last) == 0:
        redisManager.save_branch_info(repo, curr_branches)

    change = curr - last
    # print("change")
    # print(change)

    if len(change) != 0:
        print("有变化 : ", change)
        for o in change:
            # branch = o.split(":")[1].split(",")[0].replace("\"", "").strip()
            branch = o.split(":")[0].strip()
            print("branch : ", branch)
            if branch == "gh-pages":
                print("pages 无需 测试")
                continue
            res.append(branch)
    else:
        print("无变化、无需更新")
    print(res)
    return res


def update_branch(repo, modified_branches):

    # print("切换 工作 目录 ----->")
    # print("切换前:" + str(os.system("pwd")))
    # os.chdir("./" + repo.name)
    # print("切换后:" + str(os.system("pwd")))
    # switch_dir("./warehouse/" + repo.name + "_realm/" + repo.user + "/" +
    #            repo.name)

    tmp = subprocess.run("git branch",shell=True,stdout=subprocess.PIPE,encoding="utf-8",cwd="./warehouse/" + repo.name + "_realm/" + repo.user + "/" + repo.name)
    branch_res = list(map(lambda x: x.strip(),tmp.stdout.strip().split("\n")))

    for branch in modified_branches:
        for br in branch_res:
            print("匹配 ", br)
            if br.startswith("*") and branch == br.replace("*", "").strip():
                print("匹配 成功 且 当前分支 就是", branch)
                break
            if br == branch:
                print("匹配 成功 ")
                print("checkout :", branch)
                subprocess.run("git checkout " + branch,shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user + "/" + repo.name)
                break
            print("branch 匹配  失败")
        else:
            print("创建 分支 并 切换")
            subprocess.run("git checkout -b " + branch,shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user + "/" + repo.name)

        try:
            print("pulling....")
            subprocess.run("git fetch origin " + branch,shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user + "/" + repo.name)
            # res1 = os.popen("git fetch origin " + branch).readline()
            # print(res1)
            subprocess.run("git reset --hard FETCH_HEAD",shell=True,cwd="warehouse/" + repo.name + "_realm/" + repo.user + "/" + repo.name)
            # res2 = os.popen("git reset --hard FETCH_HEAD").readline()
            # print(res2)
        except:
            print("pull 不符合预期")
            return


def mark_to_test(repo, modified_branches):
    print("标记 需要 测试的 仓库 分支")
    redisManager.mark_to_test(repo, modified_branches)
    pass


def update_branch_info(repo, curr_branches):
    print("更新 仓库 info 信息")
    redisManager.update_branch_info(repo, curr_branches)
    pass


def check_for_update_available(repo):
    if redisManager.test_is_running(repo):
        print("测试 运行 中")
        print("稍后更新")
        return False
    return True


def convert_string_list(ls):
    s = []
    for l in ls:
        item = "{0}:{1}".format(l['name'], l['commit']['sha'])
        s.append(item)
    return s


# def switch_dir(path):
#     print("切换 工作 目录 ----->")
#     os.chdir(PWD)
    
#     print("切换前:")
#     subprocess.run("pwd")
#     os.chdir(path)
#     print("切换后:")
#     subprocess.run("pwd")


if __name__ == '__main__':
    main()
