# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="lib-common",
    version="0.1.0",
    description="通用Python工具库 - 网络、SSH、AI、VM",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="灵镜",
    author_email="hctj353056@gmail.com",
    url="https://github.com/hctj353056/lib-common",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "paramiko>=2.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "mypy>=0.900",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="ssh api ai network tools",
    license="MIT",
)
