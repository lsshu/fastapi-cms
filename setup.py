"""
@Time    ：2022/10/31 10:04
@Author  ：Lsshu
@File    ：setup.py
@Version ：2.0.9
@Project ：lsshu-cms
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="lsshu-cms",
      version="2.1.0",
      description="FastAPI 开发的CMS",
      python_requires=">=3.9",
      author="Lsshu",
      author_email="admin@lsshu.cn",
      url="https://github.com/lsshu/fastapi-cms",
      packages=find_packages(),
      long_description=long_description,
      long_description_content_type="text/markdown",
      license="GPLv3",
      classifiers=[
          "Programming Language :: Python :: 3.9",
          "License :: OSI Approved :: MIT License",
          "Development Status :: 3 - Alpha",
      ],
      install_requires=[
          "hashids",
          "fastapi[all]",
          "python-jose[cryptography]",
          "passlib[bcrypt]",
          "SQLAlchemy==1.4.46",
          "Pillow",
          "pymysql",
          "sqlalchemy-mptt",
          "user-agents",
          "requests",
          "openpyxl",
          "aioredis",
          "filetype",
          "pycryptodome"
      ]
      )
