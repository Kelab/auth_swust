# auth_swust

[![buddy pipeline](https://app.buddy.works/lengthmin/auth-swust/pipelines/pipeline/200365/badge.svg?token=b95b1aaea6d2d999f474a4b079f0ff2387e8767cc05e207fdf9039d3fab80695 "buddy pipeline")](https://app.buddy.works/lengthmin/auth-swust/pipelines/pipeline/200365)

## 免责声明
本代码仅用于学习，他人可使用，但开发者不承担任何责任。
请勿用于商业及违法用途。

## 安装 pytorch
如果 pip 安装 pytorch 出错，请查看官方帮助文档。  
参考 https://pytorch.org/get-started/locally/


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