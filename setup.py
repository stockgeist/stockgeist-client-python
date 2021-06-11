from setuptools import setup, find_packages

setup(
    name='stockgeist',
    version='0.1dev',
    packages=find_packages(include=['stockgeist']),
    license='MIT License',
    long_description="Python client for fetching data from StockGeist's REST API.",
)