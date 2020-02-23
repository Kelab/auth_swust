import sys
import pathlib
import setuptools
from setuptools.command.test import test as TestCommand

HERE = pathlib.Path(__file__).parent

with open(HERE / "README.md", encoding="utf-8") as f:
    README = f.read()


with open("requirements.txt") as f:
    install_requires = [line for line in f if line and line[0] not in "#-"]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["tests/"]
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


setuptools.setup(
    name="auth_swust",
    version="1.3.0",
    url="https://github.com/BuddingLab/auth_swust",
    author="BuddingLab",
    author_email="admin@maxlv.org,",
    description="auth_swust",
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
    package_data={
        "auth_swust": [
            "captcha_recognition/model/*.pth",
            "captcha_recognition/model/*.model",
        ]
    },
)
