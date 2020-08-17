import os
import redis

# 解析
## ====================
import json
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper
## ====================

# Config
## ====================
ALREADY_EXIST_REPO = "config/already_clone.yaml"
REPO_INFO = "warehouse/zCore_realm/config"
## ====================


class RedisManager:
    status = "repo_status"

    def __init__(self):
        self.redis = redis.StrictRedis()

    def repo_status(self, repos):
        exist_repo = []

        # if os.path.exists(ALREADY_EXIST_REPO):
        #     with open(ALREADY_EXIST_REPO, "r") as f:
        #         d = f.read()
        #     print(d)
        #     print("类型: ", type(d))
        #     self.exist_repo = yaml.load(d, Loader=Loader)
        #     print(self.exist_repo)

        if not self.redis.exists(self.status):
            return exist_repo
        else:
            for repo in repos:
                if self.redis.sismember(self.status, repo):
                    exist_repo.append(repo)
            return exist_repo

    def add_exist_repo(self, url):
        res = self.redis.sadd(self.status, url)
        return res

    def save_branch_info(self, repo, branches):
        key = repo.user + ":" + repo.name
        for branch in branches:
            self.redis.sadd(key, branch)

    def update_branch_info(self, repo, branches):
        key = repo.user + ":" + repo.name
        self.redis.delete(key)
        for branch in branches:
            self.redis.sadd(key, branch)

    def read_branch_info(self, repo):
        key = repo.user + ":" + repo.name
        branches = set()
        if self.redis.exists(key):
            branches = self.redis.smembers(key)
            if len(branches) != 0:
                # 多余的工作 为了 适配 字符串
                for b in branches:
                    temp = bytes.decode(b)
                    branches.remove(b)
                    branches.add(temp)
                return branches
            else:
                return branches
        else:
            return branches

    def mark_to_test(self, repo, branches):
        key = repo.user + ":" + repo.name + ":wait_to_test"
        for branch in branches:
            self.redis.sadd(key, branch)

    def test_is_running(self, repo):
        key = "running"
        repos = self.redis.lrange(key, 0, -1)
        if len(repos) != 0:
            name = repo.user + ":" + repo.name
            if name in repos:
                return True
            return False
        return False