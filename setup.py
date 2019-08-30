import setuptools

setuptools.setup(name="auth_swust",
                 version="1.0.9",
                 url='https://github.com/lengthmin/auth_swust',
                 author="BuddingLab",
                 author_email="admin@maxlv.org,",
                 description="swust auto login package",
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'beautifulsoup4>=4.7.1',
                     'Keras==2.2.4',
                     'lxml>=4.3.4',
                     'tensorflow==1.14.0',
                     'Pillow>=6.1.0',
                     'requests>=2.22.0',
                     'scikit-image>=0.15.0',
                 ],
                 classifiers=[
                     "Programming Language :: Python :: 3.6",
                     "Programming Language :: Python :: 3.7",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 package_data={
                     'auth_swust': ['captcha_recognition/model/*.model'],
                 })
