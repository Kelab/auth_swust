# auth_swust

[![buddy pipeline](https://app.buddy.works/lengthmin/auth-swust/pipelines/pipeline/200365/badge.svg?token=b95b1aaea6d2d999f474a4b079f0ff2387e8767cc05e207fdf9039d3fab80695 "buddy pipeline")](https://app.buddy.works/lengthmin/auth-swust/pipelines/pipeline/200365)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 免责声明

**请自觉遵守所在国家/地区法律法规，本程序仅供学习参考，一切法律责任由用户自己承担，与开发者无关。**

## 安装深度学习框架

使用深度学习自动识别验证码，包内自带两个模型，一个 keras 一个 pytorch 的。用户可以选用安装。
pytorch 包比较大，机器内存小的可能安不上，这时候就可以用 keras。

### 安装 pytorch

项目默认使用的是 pytorch。  
你需要安装 pytorch >= 1.2.0。  
如果 pip 安装 pytorch 出错，请查看官方帮助文档。  
参考 <https://pytorch.org/get-started/locally/>

### 安装 keras 和 tensorflow

你需要安装 keras >= 2.2.5。  
通过定义环境变量 `CAPTCHA_BACKEND` 来覆盖默认后端：

```bash
CAPTCHA_BACKEND=keras python xxxxxx
# 或者
import os
os.environ['CAPTCHA_BACKEND'] = "keras"
```

## 须知

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
