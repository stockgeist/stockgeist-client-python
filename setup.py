from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    LONG_DESC = f.read()

REQUIRED_PACKAGES = [
    'requests==2.25.1',
    'setuptools~=52.0.0',
    'numpy~=1.20.3',
    'pandas~=1.2.4',
    'tqdm~=4.61.1',
    'plotly~=4.14.3',
    'cufflinks~=0.17.3',
    'wordcloud~=1.8.1',
    'termcolor~=1.1.0',
    'python-dotenv~=0.18.0'
]

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