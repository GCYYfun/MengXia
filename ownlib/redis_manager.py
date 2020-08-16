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
            self.redis.sadd(key, json.dumps(branch))

    def read_branch_info(self, repo):
        key = repo.user + ":" + repo.name
        branches = self.redis.smembers(key)
        return branches
