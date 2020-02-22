# auth_swust

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 免责声明

**请自觉遵守所在国家/地区法律法规，本程序仅供学习参考，一切法律责任由用户自己承担，与开发者无关。**

## 开始使用

首先需要安装：

```bash
pip install auth-swust
```

```python
from auth_swust import Login
login = Login("xxxxxx", "xxxxxxx")
res, info = login.try_login()
... # 使用上面的返回值进行下一步的处理
```

### 选择深度学习框架

本项目使用深度学习自动识别验证码，包内带了两个不同框架的模型，一个 keras，一个 pytorch 的。用户可以选用框架安装。

**TIPS: pytorch 包比较大，机器内存小的可能安不上，这时候就可以用 keras。**

#### 使用 pytorch 框架

项目默认使用的是 pytorch。  
你需要安装 pytorch >= 1.2.0。  
如果 pip 安装 pytorch 出错，请查看官方帮助文档。  
参考 <https://pytorch.org/get-started/locally/>

#### 使用 keras 框架

你需要安装 keras >= 2.2.5 和 tensorflow。  
你还需要定义环境变量 `CAPTCHA_BACKEND` 为 `keras` 来设置使用。如：  

可以通过设置环境变量：

```bash
CAPTCHA_BACKEND=keras
```

或者通过 `os` 修改环境变量：

```python
import os
os.environ['CAPTCHA_BACKEND'] = "keras"
from auth_swust import Login
login = Login("xxxxxx", "xxxxxxx")
```

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
python setup.py test
```

在本地安装

```bash
python setup.py install
```

生成包:

```bash
# 按照不同系统生成
python setup.py bdist
# 生成 wheel 包
python setup.py bdist_wheel
```
