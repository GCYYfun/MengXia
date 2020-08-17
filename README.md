# 孟夏

![Logo](doc/resources/Logo.svg)

## 简介

名称 ： 孟夏

名称由来 : 因为是四月开始的 、所以叫 孟夏

目的 : 自动化测试平台

简述 :   
1. 基于 git 管理的仓库的 测试平台 

2. 不依赖于某个git平台，只需提供仓库的url、即可加入测试队列、进行测试 、

3. 测试结果与分析 会通过邮件的方式 反馈给使用者、可获得同类别项目的性能均值比较、

4. 在每次更新后的仓库 都会 重新运行 测试 、持续跟进结果 


## 项目结构

![MengXia](doc/resources/MengXia.svg)

## 前提 准备

redis

python3 

```
requests
schedule
yaml
redis
```

## 获取 孟夏

```
git clone https://github.com/GCYYfun/MengXia.git
```

## Get started


```
cd MengXia

python3 watcher.py (temp)

```