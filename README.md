# 交易引擎开发Repo说明

## 协同编辑 👨‍💻
---
IDE: [Lightly - 轻量且功能强大的集成开发工具](https://lightly.teamcode.com) 
- [Lightly 文档](https://lightly.teamcode.com/docs/introduction)
- [关联Git账号](https://lightly.teamcode.com/docs/version-control/git-relate)
注册Lightly账号后，点击以下链接自动添加至Lightly项目中：
https://lightly.teamcode.com/project/join?projectId=482192464371331072&code=296a464e


## 开发环境配置 📚
---
目前华鑫奇点的API只支持Python>3.7.4+，所以选择使用的Python版本为3.7.12
```
# 查看Python版本
~ python --version 
Python 3.7.12
``` 
相应的Django版本为3.2.0
```
# 查看Django版本
~ python -m django --version 
3.2.0
```

## 参考项目

- [vnpy华鑫柜台接口](https://github.com/vnpy/vnpy_tora) 主要可参考 ``` vnpy_tora/gateway/tora_stock_gateway.py``` 中的 ```ToraTdApi```类


## 项目结构🌳
```.
trade_engine_dev-py37
├── Pipfile 依赖管理
├── Pipfile.lock
├── README.md
├── main.py
├── tora_api Tora API文件
│   ├── __pycache__
│   │   └── traderapi.cpython-37.pyc
│   ├── _traderapi.cpython-37m-x86_64-linux-gnu.so
│   ├── document.html
│   ├── test.py
│   └── traderapi.py
└── trade_engine_app Django文件 （由 Django-admin startproject生成）
    ├── db.sqlite3
    ├── manage.py
    └── trade_engine_app
        ├── __init__.py
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py
```



## Workflow 💻

目前依赖管理使用[Pipenv](https://pipenv.pypa.io/en/latest)
```
#激活virtual env
pipenv shell
```






TODO
 
- [ ] 需不需要创建dev分支，在dev上开发完了再merge到master？
- [ ] 需要考虑下dev和production环境怎么做区分
- [ ] 到底是用django还是fastapi？fastapi可能不支持当前python版本 3.7.12
- [ ] 前端可用Next.js解决 （基于React）

## API 接口配置 


仿真账户：00032129 
交易密码：19359120
产品标识：HX5ZJ0C1PV
仿真测试环境
- 行情前置地址：tcp://210.14.72.21:4402
- 交易前置地址：tcp://210.14.72.21:4400
7x24环境
- 行情前置地址：tcp://210.14.72.16:9402
- 交易前置地址：tcp://210.14.72.15:4400



