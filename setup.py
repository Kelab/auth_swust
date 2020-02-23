import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

with open(HERE / "README.md", encoding="utf-8") as f:
    README = f.read()


with open("requirements.txt") as f:
    install_requires = [line for line in f if line and line[0] not in "#-"]


setuptools.setup(
    name="auth_swust",
    version="1.3.0",
    url="https://github.com/BuddingLab/auth_swust",
    author="BuddingLab",
    author_email="admin@maxlv.org,",
    description="模拟登录西南科技大学一站式网上服务大厅，带验证码识别",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"auth_swust": ["captcha_recognition/model/*"]},
)
