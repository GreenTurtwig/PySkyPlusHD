import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PySkyPlusHD",
    version="0.1",
    author="GreenTurtwig",
    description="Python package to control a Sky+ HD box",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GreenTurtwig/PySkyPlusHD",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License ",
        "Operating System :: OS Independent",
        "Topic :: Home Automation"
    ],
    python_requires='>=3.6',
)