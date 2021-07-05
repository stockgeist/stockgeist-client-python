![example workflow](https://github.com/stockgeist/stockgeist-client-python/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/stockgeist/stockgeist-client-python/branch/master/graph/badge.svg?token=NB0TY4LXTD)](https://codecov.io/gh/stockgeist/stockgeist-client-python)

[comment]: <> ([![Documentation Status]&#40;https://readthedocs.org/projects/stockgeist-client-python/badge/?version=latest&#41;]&#40;https://stockgeist-client-python.readthedocs.io/en/latest/?badge=latest&#41;)


# stockgeist-client-python
Python client for fetching data from StockGeist's REST API. 

The full documentation of the REST API 
can be found at [https://docs.stockgeist.ai](https://docs.stockgeist.ai).

## Installation
You can install the package directly from this repository for getting the version with the latest bug fixes and features

`pip install git+https://github.com/stockgeist/stockgeist-client-python.git`

or you can install the stable version from PyPI

`pip install stockgeist-client-python`

## Getting started
Basic usage is very straightforward. First you have to create an account with 
[StockGeist](https://dashboard.stockgeist.ai) and obtain your token for connecting to the REST API.
Then simply create an instance of `StockGeistClient` and pass your StockGeist REST API token to it:

```
import stockgeist

client = stockgeist.StockGeistClient(token="example-token")
```

Now through the `client` object you get the access to all methods for fetching data from the REST API. 
Let's say that you want to find out how many messages have been posted on social media in the last hour
about the Apple stock (NASDAQ:AAPL). All you have to do is to run the following code snippet:

```
aapl_response = client.get_message_metrics(symbol="AAPL", timeframe="1h")
print(aapl_response.as_dict)
```

Resulting output:

```
{'timestamp': ['2021-06-11 13:20:00+00:00'], 'total_count': [13.0]}
```

The `aapl_response` is an object encapsulating the data fetched from the API together with some useful 
methods to easily explore the data, e.g., plot the time series.

For now, the best source of information about the functionality of `stockgeist-client-python` are the 
docstrings inside the source files.

You can also find a sample Jupyter notebook demonstrating the possibilities of `stockgeist-client-python` in the 
`samples` directory of this project.


## Licence
This package is provided as open source under the terms of the [MIT Licence](https://opensource.org/licenses/MIT).

## Contributing
Feel free to contact us at [stockgeist@neurotechnology.com](stockgeist@neurotechnology.com) or simply 
create an issue if you would like to see additional features implemented in this package. 
