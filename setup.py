import sys
import setuptools
from setuptools.command.test import test as TestCommand

with open("requirements.txt") as f:
    install_requires = [line for line in f if line and line[0] not in "#-"]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--cov', 'tests/']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setuptools.setup(name="auth_swust",
                 version="1.0.11",
                 url='https://github.com/BuddingLab/auth_swust',
                 author="BuddingLab",
                 author_email="admin@maxlv.org,",
                 description="auth_swust",
                 packages=setuptools.find_packages(),
                 install_requires=install_requires,
                 classifiers=[
                     "Programming Language :: Python :: 3.6",
                     "Programming Language :: Python :: 3.7",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 package_data={
                     'auth_swust': ['captcha_recognition/model/*.model'],
                 })
