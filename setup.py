# coding=utf-8
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bgtask4django",
    version="1.0.1",
    author="leon_yang",
    author_email="leiyang_ace@163.com",
    description="A Django app for background task ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/leiyang23/django-bgtask",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
