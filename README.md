[![Build Status](https://travis-ci.org/{ORG-or-USERNAME}/{REPO-NAME}.png?branch=master)](https://travis-ci.org/{ORG-or-USERNAME}/{REPO-NAME})


# stockgeist-client-python
Python client for fetching data from StockGeist's REST API. 

The full documentation of the REST API 
can be found at [https://docs.stockgeist.ai](https://docs.stockgeist.ai).

## Installation
You can install the package directly from this repository:

`pip install git+https://github.com/stockgeist/stockgeist-client-python.git`

## Getting started
Basic usage is very straightforward. First you have to create an account with 
[StockGeist](https://dashboard.stockgeist.ai) and obtain your token for connecting to the REST API.
Then simply create an instance of `StockGeistClient` and pass your StockGeist REST API token to it:

```
import stockgeist

client = stockgeist.StockGeistClient(token="example-token")
```

`client = stockgeist.StockGeistClient(token="example-token")`

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


## Licence
This package is provided as open source under the terms of the [MIT Licence](https://opensource.org/licenses/MIT).

## Contributing
Feel free to contact us at [stockgeist@neurotechnology.com](stockgeist@neurotechnology.com) if you would 
like to see additional features implemented in this package.
