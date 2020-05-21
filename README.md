# auth_swust

[![PyPI](https://img.shields.io/pypi/v/auth-swust.svg)](https://pypi.python.org/pypi/auth-swust)
![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 免责声明

**请自觉遵守所在国家/地区法律法规，本程序仅供学习参考，一切法律责任由用户自己承担，与开发者无关。**

## 开始使用

安装：

```bash
pip install auth-swust
```

注意，在你开始使用之前，需要安装需要的两个[深度学习框架](https://github.com/BuddingLab/auth_swust/wiki/%E9%80%89%E6%8B%A9%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0%E6%A1%86%E6%9E%B6)**之一**！

注意，在你开始使用之前，需要安装需要的两个[深度学习框架](https://github.com/BuddingLab/auth_swust/wiki/%E9%80%89%E6%8B%A9%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0%E6%A1%86%E6%9E%B6)**之一**！

注意，在你开始使用之前，需要安装需要的两个[深度学习框架](https://github.com/BuddingLab/auth_swust/wiki/%E9%80%89%E6%8B%A9%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0%E6%A1%86%E6%9E%B6)**之一**！

例子：

```python
import os
import sys

# 设置验证码识别框架 需要先安装 tensorflow>=2.1.0
os.environ['CAPTCHA_BACKEND'] = "keras"
from loguru import logger
from auth_swust import Login, default_logger

# 设置 log 等级
logger.remove(default_logger)
logger.add(sys.stdout, level="DEBUG")

login = Login("xxxxxx", "xxxxxxx")
res, info = login.try_login(login_other=True)
# 使用上面的返回值进行下一步的处理
# 具体返回值类型可以查看代码 try_login 的注释
if res:
    print(info)
```

如果你想设置 log 等级，请查看: [设置 LOG](https://github.com/BuddingLab/auth_swust/wiki/%E8%AE%BE%E7%BD%AE-LOG)

[FAQ点我点我](https://github.com/BuddingLab/auth_swust/wiki/FAQ)

## 开发须知

开发前安装依赖  

```bash
pip install -r requirements.txt
```

测试所需依赖：

```bash
pip install -r dev/requirements_test.txt
```

测试：

```bash
pytest
```

在本地安装

```bash
python setup.py install
```

生成包:

```bash
python setup.py sdist bdist_wheel
```
