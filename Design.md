# Meng Xia Design


测试 行为

配置 测试 用例 


测试 用例 

仓库


# 使用 git bisect 发现 错误 commit

设计 函数 find fault

处于 一个 分支

git log 获取 记录 、指定 开始 结束 commit id

开始 测试 使用 git bisect

测试逻辑 写成一个 函数 、 返回值 为bool

写一个 执行 git bisect good and git bisect bad 的 函数 接收 bool

反复 执行

二分 结束 后 找到 第一次 错误 引进的 commit id  

执行 git bisect reset

返回 id



TODO
