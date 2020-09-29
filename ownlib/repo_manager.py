# 解析
## ====================
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

# Config
## ====================
REPO_LIST = "config/repo_list.yaml"
ALREADY_EXIST_REPO = "config/already_clone.yaml"
REPO_INFO = "warehouse/zCore_realm/config"
PWD = "/home/own/MengXia"
## ====================

redis = rdm.RedisManager()


class Repo:
    def __init__(self, url):
        (user, name) = self.analyzing_url(url)
        self.url = url
        self.user = user
        self.name = name

    def analyzing_url(self, url):
        user = url.split("/")[3].strip()
        repo = url.split("/")[4].strip()
        return (user, repo)


class RepoManager:

    repos = []
    repos_url = []
    already_exist_repo = set()
    already_exist_repo_url = []

    def __init__(self):
        with open(REPO_LIST, "r") as f:
            d = f.read()

        print(d)

        self.repos_url = yaml.load(d, Loader=Loader)
        print(self.repos_url)
        print("读取 仓库 url 列表 完成 ")

        print("全部需要观测的仓库：")
        for repo_name in self.repos_url:
            for repo in self.repos_url[repo_name]:
                r = Repo(repo)
                self.repos.append(r)
                print("仓库： ", r.user, "-", r.name)
        print("仓库 列表 完成")

        self.already_exist_repo_url = redis.repo_status(self.repos_url)

        if len(self.already_exist_repo_url) != 0:
            for exist_repo in self.already_exist_repo_url:
                r = Repo(exist_repo)
                self.already_exist_repo.add(r.url)
                print(r.user, ":", r.name, " 已clone完毕")

        print("存在 仓库 列表 完成")