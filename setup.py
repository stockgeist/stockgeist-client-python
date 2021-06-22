from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    LONG_DESC = f.read()

with open("requirements.txt", "r") as f:
    REQUIRED_PACKAGES = f.readlines()

setup(
    name="stockgeist",
    version="0.1",
    description="StockGeist's REST API Python client.",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    url="https://github.com/stockgeist/stockgeist-client-python",
    project_urls={
        "Bug Tracker": "https://github.com/stockgeist/stockgeist-client-python/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=['stockgeist']),
    install_requires=REQUIRED_PACKAGES,
    python_requires=">=3.6",
)